from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class AvailableProjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_enable=True)


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
    first_name = None
    last_name = None
    
    email = models.EmailField(verbose_name=_('Email Address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Project(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='projects')
    api_key = models.CharField(verbose_name=_('API Key'), max_length=settings.API_KEY_LENGTH, blank=True, null=True, unique=True)
    name = models.CharField(verbose_name=_('Name'), max_length=32)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=32, unique=True)
    description = models.TextField(verbose_name=_('Description'), blank=True)
    website = models.URLField(verbose_name=_('Website'), blank=True)
    is_enable = models.BooleanField(verbose_name=_('Is Enable'), default=True)
    created_time = models.DateTimeField(verbose_name=_('Created Time'), auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name=_('Updated Time'), auto_now=True)

    objects = models.Manager()
    available_objects = AvailableProjectManager()

    class Meta:
        db_table = 'projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.slug

    @staticmethod
    def get_project_object_by_api_key(api_key):
        if not api_key:
            return None
        try:
            project = Project.available_objects.get(api_key=api_key)
        except Project.DoesNotExist:
            return None
        else:
            return project


class KibanaAccess(models.Model):
    project = models.OneToOneField(verbose_name=_('Project'), to=Project,
                                   on_delete=models.CASCADE, related_name='kibana_access')
    username = models.CharField(verbose_name=_('Username'), max_length=254, unique=True)
    password = models.CharField(verbose_name=_('Password'), max_length=64)
    is_dashboard_created = models.BooleanField(verbose_name=_('Is Dashboard Created'), default=False)
    created_time = models.DateTimeField(verbose_name=_('Created Time'), auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name=_('Updated Time'), auto_now=True)

    class Meta:
        db_table = 'kibana_accesses'
        verbose_name = _('Kibana Access')
        verbose_name_plural = _('Kibana Accesses')

    def __str__(self):
        return self.username
