# Generated by Django 3.2.15 on 2022-09-01 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_uuid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='Project UUID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('slug', models.SlugField(max_length=32, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Time')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='Updated Time')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='KibanaAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True, verbose_name='Username')),
                ('password', models.CharField(max_length=64, verbose_name='Password')),
                ('is_dashboard_created', models.BooleanField(default=False, verbose_name='Is Dashboard Created')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Time')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='Updated Time')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kibana_access', to='core.project', verbose_name='Project')),
            ],
            options={
                'verbose_name': 'Kibana Access',
                'verbose_name_plural': 'Kibana Accesses',
                'db_table': 'kibana_accesses',
            },
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=64, unique=True, verbose_name='API Key')),
                ('is_revoked', models.BooleanField(default=False, verbose_name='Is Revoked')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Time')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='Updated Time')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'API Key',
                'verbose_name_plural': 'API Keys',
                'db_table': 'api_keys',
            },
        ),
    ]