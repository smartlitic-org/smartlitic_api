from django.conf import settings

from elasticsearch_dsl import connections


class ElasticsearchConnector(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ElasticsearchConnector, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        print(settings.ELASTICSEARCH_URL)
        self.connection = connections.create_connection(
            hosts=[settings.ELASTICSEARCH_URL],
            timeout=settings.ELASTICSEARCH_TIMEOUT,
        )

    def get_connection(self):
        return self.connection
