# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('muo', '0018_auto_20150628_0356'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuereport',
            name='resolve_reason',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='issuereport',
            name='reviewed_at',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='issuereport',
            name='reviewed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='issuereport',
            name='status',
            field=models.CharField(default=b'open', max_length=64, choices=[(b'open', b'Open'), (b'investigating', b'Investigating'), (b'reopen', b'Re-open'), (b'resolved', b'Resolved')]),
        ),
    ]
