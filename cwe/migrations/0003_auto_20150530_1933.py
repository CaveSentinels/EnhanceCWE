# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0002_cwedescription'),
    ]

    operations = [
        migrations.CreateModel(
            name='DesignFlaw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('flawName', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'DesignFlaw',
                'verbose_name_plural': 'DesignFlaw',
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('flawName', models.TextField(null=True, blank=True)),
                ('designFlaw', models.ManyToManyField(related_name='designflaw', to='cwe.DesignFlaw')),
            ],
            options={
                'verbose_name': 'Tags',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.DeleteModel(
            name='CWEDescription',
        ),
    ]
