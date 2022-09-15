from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth import LoggerAuthentication
from core.models import ComponentLog

from utils.connectors import ElasticsearchConnector

from .serializers import LoggerLoadCompleteSerializer, LoggerRateSerializer

elasticsearch_connector = ElasticsearchConnector()


class LoggerBaseView(APIView):
    authentication_classes = [LoggerAuthentication]

    def extra_params(self, request):
        return {
            'user_id': request.user.id,
            'project_uuid': request.auth.project_uuid,
            'project_slug': request.auth.slug,
            'event_type': self.event_type,
        }

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_log_model = serializer.validated_data.pop('target_log_model')

        log_data = {
            **self.extra_params(request),
            **serializer.validated_data,
        }
        if target_log_model is ComponentLog:
            log_data.update(**log_data['component'])
            del log_data['component']

        log = target_log_model(**log_data)
        log.save(using=elasticsearch_connector.get_connection())

        return Response()


class LoggerLoadCompleteView(LoggerBaseView):
    serializer_class = LoggerLoadCompleteSerializer
    event_type = 'LOAD_COMPLETE'


class LoggerRateView(LoggerBaseView):
    serializer_class = LoggerRateSerializer
    event_type = 'RATE'
