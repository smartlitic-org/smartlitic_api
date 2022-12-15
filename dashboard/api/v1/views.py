import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, A

from logger.models import LoggerModel
from users.permissions import IsProjectBelongToUser
from utils.connectors import ElasticsearchConnector

from .serializers import DashboardGeneralSerializer

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


class DashboardGeneralView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & IsProjectBelongToUser]
    serializer_class = DashboardGeneralSerializer

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
    def generate_chart_data(elasticsearch_search_query):
        chart_data = {
            'labels': [],
            'data': []
        }
        try:
            result = elasticsearch_search_query.execute()
        except NotFoundError:
            return chart_data
        for bucket in result.aggregations.group_by.buckets:
            if hasattr(bucket, 'key_as_string'):
                chart_data['labels'].append(bucket.key_as_string)
            else:
                chart_data['labels'].append(bucket.key)
            chart_data['data'].append(bucket.doc_count)
        return chart_data

    def create_session_device_chart(self, user_id, project_id, index_name, start_time, end_time):
        search_query = self.generate_search_query(user_id, project_id, index_name,
                                                  start_time, end_time, 'LOAD_COMPLETE', 'GENERAL')
        client_device_types = A('terms', field='client_device_type')
        search_query.aggs.bucket('group_by', client_device_types)
        return self.generate_chart_data(search_query)

    def create_audience_overview_chart(self, user_id, project_id, index_name, report_type, start_time, end_time):
        search_query = self.generate_search_query(user_id, project_id, index_name,
                                                  start_time, end_time, 'LOAD_COMPLETE', 'GENERAL')
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
        return self.generate_chart_data(search_query)

    def get(self, request, project_id):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        report_type = serializer.validated_data['report_type']
        if report_type == 'today':
            start_time = datetime.datetime.now().date()
            end_time = start_time + datetime.timedelta(days=1)
        else:
            start_time = serializer.validated_data['report_from']
            end_time = serializer.validated_data['report_until']

        user_id = request.user.id
        logger_index = LoggerModel.get_index_name(user_id, project_id)
        result = {
            'sessions_device': self.create_session_device_chart(
                user_id, project_id, logger_index, start_time, end_time
            ),
            'audience_overview': self.create_audience_overview_chart(
                user_id, project_id, logger_index, report_type, start_time, end_time
            )
        }
        return Response(result)
