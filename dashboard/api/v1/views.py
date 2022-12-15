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
    def create_session_device_chart(user_id, project_id, index_name, start_time, end_time):
        search_query = Search(using=elasticsearch_connector.get_connection(), index=index_name)
        search_query = search_query.filter('term', user_id=user_id)
        search_query = search_query.filter('term', project_id=project_id)
        search_query = search_query.filter('term', event_type='LOAD_COMPLETE')
        search_query = search_query.filter('term', log_type='GENERAL')
        search_query = search_query.filter('range', created_time={'gte': start_time, 'lt': end_time})

        client_device_types = A('terms', field='client_device_type')
        search_query.aggs.bucket('client_device_types', client_device_types)

        chart_data = {'labels': [], 'data': []}
        try:
            result = search_query.execute()
        except NotFoundError:
            return chart_data
        for bucket in result.aggregations.client_device_types.buckets:
            chart_data['labels'].append(bucket.key)
            chart_data['data'].append(bucket.doc_count)

        return chart_data

    def get(self, request, project_id):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['report_type'] == 'today':
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
        }
        return Response(result)
