import datetime

from collections import OrderedDict
from dateutil.parser import parse

from django.utils import timezone

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
    def generate_search_query(user_id, project_id, index_name, start_time, end_time, event_type, log_type):
        search_query = Search(using=elasticsearch_connector.get_connection(), index=index_name)
        search_query = search_query.filter('term', user_id=user_id)
        search_query = search_query.filter('term', project_id=project_id)
        search_query = search_query.filter('term', event_type=event_type)
        search_query = search_query.filter('term', log_type=log_type)
        search_query = search_query.filter('range', created_time={'gte': start_time, 'lt': end_time})
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
            return chart_data if not dict_response else {}
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
    def generate_raw_data(elasticsearch_search_query):
        raw_data = []
        try:
            result = elasticsearch_search_query.execute()
        except NotFoundError:
            return raw_data
        for item in result.hits.hits:
            raw_data.append(item._source.client_comment)
        return raw_data

    def create_session_device_chart(self, user_id, project_id, index_name, start_time, end_time, log_type):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type
        )
        client_device_types = A('terms', field='client_device_type')
        search_query.aggs.bucket('group_by', client_device_types)
        return self.generate_chart_data(search_query)

    def create_audience_overview_chart(self, user_id, project_id, index_name,
                                       report_type, start_time, end_time, log_type):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type
        )
        if report_type == 'today':
            aggregate_params = {
                'field': 'created_time',
                'interval': 'hour',
                'format': 'k',
            }
        else:
            aggregate_params = {
                'field': 'created_time',
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

    def create_numeric_metrics_data(self, user_id, project_id, index_name, start_time, end_time, log_type):
        visitors_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'LOAD_COMPLETE',
            log_type
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
            log_type
        )
        avg_user_rating = A('avg', field='client_rate', missing=0)
        avg_user_rating_query.aggs.bucket('group_by', avg_user_rating)
        avg_user_rating_result = self.generate_chart_data(avg_user_rating_query, return_aggregation_result=True)

        max_user_rating_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'RATE',
            log_type
        )
        max_user_rating = A('max', field='client_rate', missing=0)
        max_user_rating_query.aggs.bucket('group_by', max_user_rating)
        max_user_rating_result = self.generate_chart_data(max_user_rating_query, return_aggregation_result=True)

        return {
            'total_clicks': visitors_query.count() if unique_visitors else 0,
            'unique_visitors': unique_visitors,
            'avg_user_rating': f'{avg_user_rating_result:.2f}',
            'max_user_rating': f'{max_user_rating_result:.2f}',
        }

    def create_comments_data(self, user_id, project_id, index_name, start_time, end_time, log_type):
        search_query = self.generate_search_query(
            user_id,
            project_id,
            index_name,
            start_time,
            end_time,
            'RATE',
            log_type
        )
        search_query = search_query.exclude('term', client_comment='')
        return self.generate_raw_data(search_query)

    def get(self, request, project_id):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        log_type = 'GENERAL' if not serializer.validated_data.get('component') else 'COMPONENT'

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
                user_id, project_id, logger_index, start_time, end_time, log_type
            ),
            'audience_overview': self.create_audience_overview_chart(
                user_id, project_id, logger_index, report_type, start_time, end_time, log_type
            ),
            'numeric_metrics': self.create_numeric_metrics_data(
                user_id, project_id, logger_index, start_time, end_time, log_type
            ),
        }
        if log_type == 'COMPONENT':
            result['comments'] = self.create_comments_data(
                user_id, project_id, logger_index, start_time, end_time, log_type
            )
        return Response(result)


class DashboardGeneralView(DashboardBaseView):
    serializer_class = DashboardGeneralSerializer


class DashboardComponentsView(DashboardBaseView):
    serializer_class = DashboardComponentSerializer
