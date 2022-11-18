from django.utils import timezone
from elasticsearch_dsl import (
    Document,
    Date,
    Keyword,
    Text,
    Byte,
    Float,
    Ip,
    Long,
)


class LoggerModel(Document):
    user_id = Keyword()
    project_id = Keyword()
    absolute_uri = Text()
    event_type = Keyword()
    log_type = Keyword()
    route = Text()
    created_time = Date()

    client_rate = Byte()
    client_comment = Text()

    component_id = Keyword()
    component_type = Keyword()
    component_inner_text = Text()

    client_uuid = Keyword()
    client_device_type = Keyword()
    client_platform = Text()
    client_public_ip_address = Ip()
    client_os = Text()
    client_browser = Text()
    client_browser_version = Text()
    client_language = Text()
    client_screen_size = Text()
    client_document_referrer = Text()
    client_timezone = Text()
    client_timezone_offset = Float()
    client_timestamp = Long()

    def save(self, **kwargs):
        self.created_time = timezone.now()
        kwargs['index'] = f'smartlitic_logs-{self.user_id}-{self.project_id}'
        return super().save(**kwargs)
    
    class Index:
        name = 'smartlitic_logs-*-*'
