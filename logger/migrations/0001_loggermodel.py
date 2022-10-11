from django.db import migrations

from logger.models import LoggerModel

from utils.connectors import ElasticsearchConnector
from utils.elasticsearch import save_index_template_as_composable


def initial_logger_model_index_template(apps, schema_editor):
    elasticsearch_connector = ElasticsearchConnector()
    logger_model_template = LoggerModel._index.as_template('smartlitic_logs', order=0)
    save_index_template_as_composable(logger_model_template, elasticsearch_connector.get_connection())
    return True


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_logger_model_index_template),
    ]
