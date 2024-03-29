import datetime

from collections import OrderedDict
from dateutil.parser import parse

from django.utils import timezone
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, A

from logger.models import LoggerModel
from users.permissions import IsProjectBelongToUser
from utils.connectors import ElasticsearchConnector

from .serializers import DashboardGeneralSerializer, DashboardComponentSerializer

elasticsearch_connector = ElasticsearchConnector()


class ComponentsListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & IsProjectBelongToUser]

    def get(self, request, project_id):
        index = LoggerModel.get_index_name(request.user.id, project_id)
        search_query = Search(using=elasticsearch_connector.get_connection(), index=index)
        search_query = search_query.filter('term', project_id=project_id)
        search_query = search_query.exclude('term', component_id='')

        unique_components = A('terms', field='component_id')
        search_query.aggs.bucket('unique_components', unique_components)
        try:
            result = search_query.execute()
        except NotFoundError:
            return Response([])
        return Response([item.key for item in result.aggregations.unique_components.buckets])


class DashboardBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & IsProjectBelongToUser]

    @staticmethod
    def convert_dict_to_chart_data(chart_dict_data, datetime_sort=False):
        parser_func = int
        if datetime_sort:
            parser_func = parse

        sorted_data = OrderedDict(sorted(chart_dict_data.items(), key=lambda x: parser_func(x[0])))
        chart_data = {
            'labels': [],
            'data': [],
        }
        for key_name, value in sorted_data.items():
            chart_data['labels'].append(key_name)
            chart_data['data'].append(value)
        return chart_data

    @staticmethod
    def generate_search_query(user_id, project_id, index_name, start_time, end_time, event_type, log_type, component):
        search_query = Search(using=elasticsearch_connector.get_connection(), index=index_name)
        search_query = search_query.filter('term', user_id=user_id)
        search_query = search_query.filter('term', project_id=project_id)
        search_query = search_query.filter('term', event_type=event_type)
        search_query = search_query.filter('term', log_type=log_type)

        range_filter = {}
        if start_time:
            range_filter['gte'] = start_time
        if end_time:
            range_filter['lte'] = end_time

        search_query = search_query.filter('range', created_time=range_filter)

        if component:
            search_query = search_query.filter('term', component_id=component)

        return search_query

    @staticmethod
    def generate_chart_data(elasticsearch_search_query, dict_response=False, return_aggregation_result=False):
        chart_data = {
            'labels': [],
            'data': [],
        }
        try:
            result = elasticsearch_search_query.execute()
        except NotFoundError:
            return 0 if return_aggregation_result else {} if dict_response else chart_data
        if return_aggregation_result:
            return result.aggregations.group_by.value
        for bucket in result.aggregations.group_by.buckets:
            if hasattr(bucket, 'key_as_string'):
                chart_data['labels'].append(bucket.key_as_string)
            else:
                chart_data['labels'].append(bucket.key)
            chart_data['data'].append(bucket.doc_count)

        if not dict_response:
            return chart_data

        chart_dict_data = {}
        for index in range(len(chart_data['data'])):
            chart_dict_data[chart_data['labels'][index]] = chart_data['data'][index]
        return chart_dict_data

    @staticmethod
    def generate_raw_comments_data(elasticsearch_search_query):
        raw_data = []
        try:
            result = elasticsearch_search_query.execute()
        except NotFoundError:
            return raw_data
        for item in result.hits.hits:
            raw_data.append({
                'comment': item._source.client_comment,
                'rate': item._source.client_rate,
            })
        return raw_data

    def create_session_device_chart(self, user_id, project_id, index_name, start_time, end_time, log_type, component):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type,
            component
        )
        client_device_types = A('terms', field='client_device_type')
        search_query.aggs.bucket('group_by', client_device_types)
        return self.generate_chart_data(search_query)

    def create_audience_overview_chart(self, user_id, project_id, index_name, report_type,
                                       start_time, end_time, log_type, component):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type,
            component
        )
        if report_type == 'today':
            aggregate_params = {
                'field': 'created_time',
                'time_zone': 'Asia/Tehran',
                'interval': 'hour',
                'format': 'k',
            }
        else:
            aggregate_params = {
                'field': 'created_time',
                'time_zone': 'Asia/Tehran',
                'interval': 'day',
                'format': 'yyy-MM-dd',
            }

        group_by_day = A('date_histogram', **aggregate_params)
        search_query.aggs.bucket('group_by', group_by_day)

        chart_dict_data: dict = self.generate_chart_data(search_query, dict_response=True)

        if not chart_dict_data:
            return {'labels': [], 'data': []}

        convert_kwargs = {}
        if report_type == 'today':
            now_hour = timezone.now().hour
            for hour in range(0, now_hour + 1):
                hour = str(hour)
                if hour not in chart_dict_data.keys():
                    chart_dict_data[hour] = 0
        else:
            convert_kwargs.update(datetime_sort=True)
            generated_times = []
            tmp_time = start_time
            while tmp_time <= end_time:
                generated_times.append(tmp_time)
                tmp_time += datetime.timedelta(days=1)
            for generated_time in generated_times:
                generated_time = str(generated_time)
                if generated_time not in chart_dict_data.keys():
                    chart_dict_data[generated_time] = 0

        return self.convert_dict_to_chart_data(chart_dict_data, **convert_kwargs)

    def create_numeric_metrics_data(self, user_id, project_id, index_name, start_time, end_time, log_type, component):
        visitors_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type,
            component
        )
        client_uuids = A('terms', field='client_uuid')
        visitors_query.aggs.bucket('group_by', client_uuids)
        unique_visitors = self.generate_chart_data(visitors_query)
        unique_visitors = len(unique_visitors['data'])

        avg_user_rating_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'RATE',
            log_type,
            component
        )
        avg_user_rating = A('avg', field='client_rate', missing=0)
        avg_user_rating_query.aggs.bucket('group_by', avg_user_rating)
        avg_user_rating_result = self.generate_chart_data(avg_user_rating_query, return_aggregation_result=True) or 0

        total_clicks = visitors_query.count() if unique_visitors else 0
        result = {
            'total_clicks': total_clicks,
            'unique_visitors': unique_visitors,
            'avg_user_rating': f'{avg_user_rating_result:.2f}',
        }

        if component:
            conversion_rate = unique_visitors / total_clicks if not total_clicks == 0 else 0
            result['conversion_rate'] = f'{conversion_rate:.2f}',
        else:
            new_users = 0
            if total_clicks != 0:
                other_days_query = self.generate_search_query(
                    user_id,
                    project_id,
                    index_name,
                    None,
                    start_time - datetime.timedelta(days=1),
                    'LOAD_COMPLETE',
                    log_type,
                    component
                )
                other_days_data = other_days_query[:settings.ELASTICSEARCH_QUERY_SIZE].execute()
                other_days_per_day = {}
                for data in other_days_data:
                    date_str = data.created_time.split('T')[0]
                    date_data = other_days_per_day.get(date_str, set())
                    date_data.add(data.client_uuid)
                    other_days_per_day[date_str] = date_data

                report_data = self.generate_search_query(
                    user_id,
                    project_id,
                    index_name,
                    start_time,
                    end_time,
                    'LOAD_COMPLETE',
                    log_type,
                    component
                )
                report_data_query = report_data[:settings.ELASTICSEARCH_QUERY_SIZE].execute()

                report_users = set()
                for data in report_data_query:
                    report_users.add(data.client_uuid)

                if not other_days_data:
                    new_users = unique_visitors
                elif report_users:
                    new_users = set()
                    for report_user in report_users:
                        for per_date_data in other_days_per_day.values():
                            if report_user not in per_date_data:
                                new_users.add(report_user)
                    new_users = len(new_users)

            result['new_users'] = new_users

        return result

    def create_comments_data(self, user_id, project_id, index_name, start_time, end_time, log_type, component):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'RATE',
            log_type,
            component
        )
        search_query = search_query.exclude('term', client_comment='')
        search_query = search_query.sort({'client_timestamp': {'order': 'desc'}})
        return self.generate_raw_comments_data(search_query)

    def get(self, request, project_id):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        log_type = 'GENERAL'
        component = serializer.validated_data.get('component')
        if component:
            log_type = 'COMPONENT'

        report_type = serializer.validated_data['report_type']
        if report_type == 'today':
            start_time = timezone.now().date()
            end_time = start_time + datetime.timedelta(days=1)
        else:
            start_time = serializer.validated_data['report_from']
            end_time = serializer.validated_data['report_until']

        user_id = request.user.id
        logger_index = LoggerModel.get_index_name(user_id, project_id)
        result = {
            'sessions_device': self.create_session_device_chart(
                user_id, project_id, logger_index, start_time, end_time, log_type, component=component
            ),
            'audience_overview': self.create_audience_overview_chart(
                user_id, project_id, logger_index, report_type, start_time, end_time, log_type, component=component
            ),
            'numeric_metrics': self.create_numeric_metrics_data(
                user_id, project_id, logger_index, start_time, end_time, log_type, component=component
            ),
        }
        if log_type == 'COMPONENT':
            result['comments'] = self.create_comments_data(
                user_id, project_id, logger_index, start_time, end_time, log_type, component=component
            )
        return Response(result)


class DashboardGeneralView(APIView):

    def get(self, request, project_id):
        numberic_result = {
                'total_clicks': 2336,
                'unique_visitors': 4705,
                'avg_user_rating': 4.2,
                 "new_users": 1830,
            }
        sessions_device_result = {
            'labels': ["DESKTOP", "MOBILE"],
            'data' : [1518,818]
        }
        audience_result =  {
            "labels": [
                "2023-10-26",
                "2023-10-27",
                "2023-10-28",
                "2023-10-29",
                "2023-10-30",
                "2023-10-31",
                "2023-11-01",
                "2023-11-02",
                "2023-11-03",
                "2023-11-04",
                "2023-11-05",
                "2023-11-06",
                "2023-11-07",
                "2023-11-08",
                "2023-11-09",
                "2023-11-10",
                "2023-11-11",
                "2023-11-12",
                "2023-11-13",
                "2023-11-14",
                "2023-11-15",
                "2023-11-16",
                "2023-11-17",
                "2023-11-18",
                "2023-11-19",
                "2023-11-20",
                "2023-11-21",
                "2023-11-22",
                "2023-11-23",
                "2023-11-24",
                "2023-11-25"
            ],
            "data":[73, 74, 90, 67, 80, 99, 87, 73, 81, 69, 61, 87, 76, 96, 82, 85, 61, 58, 100, 56, 81, 87, 84, 96, 74, 78, 87, 58, 53, 57]
        }
        result = {
            'numeric_metrics': numberic_result,
            'sessions_device': sessions_device_result,
            'audience_overview': audience_result
        }
        return Response(result)
    # serializer_class = DashboardGeneralSerializer


# class DashboardComponentsView(DashboardBaseView):
#     serializer_class = DashboardComponentSerializer

class DashboardComponentsView(APIView):
    def get(self, request, project_id):
        numberic_result = {
            "total_clicks": 658,
            "unique_visitors": 1459,
            "avg_user_rating": "3.8",
            "conversion_rate": [
                "45%"
            ]
        }
        audience_result =  {
            "labels": [
                "2023-10-26",
                "2023-10-27",
                "2023-10-28",
                "2023-10-29",
                "2023-10-30",
                "2023-10-31",
                "2023-11-01",
                "2023-11-02",
                "2023-11-03",
                "2023-11-04",
                "2023-11-05",
                "2023-11-06",
                "2023-11-07",
                "2023-11-08",
                "2023-11-09",
                "2023-11-10",
                "2023-11-11",
                "2023-11-12",
                "2023-11-13",
                "2023-11-14",
                "2023-11-15",
                "2023-11-16",
                "2023-11-17",
                "2023-11-18",
                "2023-11-19",
                "2023-11-20",
                "2023-11-21",
                "2023-11-22",
                "2023-11-23",
                "2023-11-24",
                "2023-11-25"
            ],
            "data":[19, 28, 16, 24, 21, 29, 16, 20, 31, 11, 29, 13, 11, 19, 23, 18, 15, 24, 31, 18, 27, 11, 15, 27, 17, 12, 18, 14, 19, 24]
        }
        
        comments_result = [
            {
                "comment": "it's ok but maybe highlight it more?",
                "rate": 4
            },
            {
                "comment": "nice button, easy to find",
                "rate": 5
            },
            {
                "comment": "I was looking for pricing section and couldn't find it",
                "rate": 1
            },
            {
                "comment": "I don't like the white color and blue backgroud",
                "rate": 3
            }
        ]
        sessions_device_result = {
            'labels': ["DESKTOP", "MOBILE"],
            'data' : [422,236]
        }
        result = {
            'numeric_metrics': numberic_result,
            'sessions_device': sessions_device_result,
            "audience_overview": audience_result,
            "comments": comments_result
        }
        return Response(result)

