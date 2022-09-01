from django.db import migrations

from core.models import GeneralLog, ComponentLog
from utils.connectors import ElasticsearchConnector


def initial_general_logs_index(apps, schema_editor):
    elasticsearch_connector = ElasticsearchConnector()
    GeneralLog.init(using=elasticsearch_connector.get_connection())
    return True

def initial_component_logs_index(apps, schema_editor):
    elasticsearch_connector = ElasticsearchConnector()
    ComponentLog.init(using=elasticsearch_connector.get_connection())
    return True


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_apikey_kibanaaccess_project'),
    ]

    operations = [
        migrations.RunPython(initial_general_logs_index),
        migrations.RunPython(initial_component_logs_index),
    ]
