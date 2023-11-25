from rest_framework.response import Response
from rest_framework.views import APIView

from smartlitic_api.auth import SDKAuthentication
from utils.connectors import ElasticsearchConnector
from logger.models import LoggerModel

from .serializers import LoggerLoadCompleteSerializer, LoggerRateSerializer

elasticsearch_connector = ElasticsearchConnector()


class LoggerBaseView(APIView):
    authentication_classes = [SDKAuthentication]

    def extra_params(self, request):
        return {
            'user_id': request.user.id,
            'project_id': request.auth.id,
            'event_type': self.event_type,
        }

#adding a comment here
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        log_type = serializer.validated_data.get('log_type')

        log_data = {
            **self.extra_params(request),
            **serializer.validated_data,
        }
        if log_type == 'COMPONENT':
            log_data.update(**log_data['component'])
            del log_data['component']

        log = LoggerModel(**log_data)
        # log.save(using=elasticsearch_connector.get_connection())

        return Response()


class LoggerLoadCompleteView(LoggerBaseView):
    serializer_class = LoggerLoadCompleteSerializer
    event_type = 'LOAD_COMPLETE'


class LoggerRateView(LoggerBaseView):
    serializer_class = LoggerRateSerializer
    event_type = 'RATE'
