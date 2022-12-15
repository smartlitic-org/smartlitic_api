# Generated by Django 3.2.15 on 2022-11-18 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20221026_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='project_uuid',
        ),
        migrations.AddField(
            model_name='project',
            name='api_key',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='API Key'),
        ),
        migrations.AlterField(
            model_name='kibanaaccess',
            name='username',
            field=models.CharField(max_length=254, unique=True, verbose_name='Username'),
        ),
        migrations.DeleteModel(
            name='APIKey',
        ),
    ]