from uuid import uuid4

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The given email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name=_('Email Address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Project(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='projects')
    project_uuid = models.UUIDField(verbose_name=_('Project UUID'), default=uuid4, unique=True)
    name = models.CharField(verbose_name=_('Name'), max_length=32)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=32, unique=True)
    description = models.TextField(verbose_name=_('Description'), blank=True)
    website = models.URLField(verbose_name=_('Website'), blank=True)
    created_time = models.DateTimeField(verbose_name=_('Created Time'), auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name=_('Updated Time'), auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


class KibanaAccess(models.Model):
    project = models.OneToOneField(verbose_name=_('Project'), to=Project,
                                   on_delete=models.CASCADE, related_name='kibana_access')
    username = models.CharField(verbose_name=_('Username'), max_length=32, unique=True)
    password = models.CharField(verbose_name=_('Password'), max_length=64)
    is_dashboard_created = models.BooleanField(verbose_name=_('Is Dashboard Created'), default=False)
    created_time = models.DateTimeField(verbose_name=_('Created Time'), auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name=_('Updated Time'), auto_now=True)

    class Meta:
        db_table = 'kibana_accesses'
        verbose_name = _('Kibana Access')
        verbose_name_plural = _('Kibana Accesses')


class APIKey(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='api_keys')
    api_key = models.CharField(verbose_name=_('API Key'), max_length=64, unique=True)
    is_revoked = models.BooleanField(verbose_name=_('Is Revoked'), default=False)
    created_time = models.DateTimeField(verbose_name=_('Created Time'), auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name=_('Updated Time'), auto_now=True)

    class Meta:
        db_table = 'api_keys'
        verbose_name = _('API Key')
        verbose_name_plural = _('API Keys')
