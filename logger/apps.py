from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logger'
    verbose_name = _('Logger')
    verbose_name_plural = _('Logger')
