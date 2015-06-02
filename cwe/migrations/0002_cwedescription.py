# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CWEDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(unique=True, max_length=32)),
            ],
            options={
                'verbose_name': 'CWEDescription',
                'verbose_name_plural': 'CWEDescription',
            },
        ),
    ]
