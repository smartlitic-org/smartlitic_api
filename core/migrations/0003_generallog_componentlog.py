from django.db import migrations

from core.models import GeneralLog, ComponentLog

from utils.connectors import ElasticsearchConnector
from utils.elasticsearch import save_index_template_as_composable


def initial_general_logs_index_template(apps, schema_editor):
    elasticsearch_connector = ElasticsearchConnector()
    general_logs_template = GeneralLog._index.as_template(GeneralLog.base_index_name, order=0)
    save_index_template_as_composable(general_logs_template, elasticsearch_connector.get_connection())
    return True

def initial_component_logs_index_template(apps, schema_editor):
    elasticsearch_connector = ElasticsearchConnector()
    components_logs_template = ComponentLog._index.as_template(ComponentLog.base_index_name, order=0)
    save_index_template_as_composable(components_logs_template, elasticsearch_connector.get_connection())
    return True


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_apikey_kibanaaccess_project'),
    ]

    operations = [
        migrations.RunPython(initial_general_logs_index_template),
        migrations.RunPython(initial_component_logs_index_template),
    ]
