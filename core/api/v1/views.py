from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth import LoggerAuthentication
from core.models import ComponentLog

from utils.connectors import ElasticsearchConnector

from .serializers import LoggerClickSerializer

elasticsearch_connector = ElasticsearchConnector()


class LoggerClickView(APIView):
    authentication_classes = [LoggerAuthentication]
    serializer_class = LoggerClickSerializer
    event_type = 'CLICK'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_log_model = serializer.validated_data.pop('target_log_model')

        log_data = {
            **serializer.validated_data
        }
        if target_log_model is ComponentLog:
            log_data.update(**log_data['component'])
            del log_data['component']

        log = target_log_model(**log_data)
        log.save(using=elasticsearch_connector.get_connection())

        return Response()
