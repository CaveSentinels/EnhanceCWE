# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0018_auto_20150628_0356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuereport',
            name='status',
            field=models.CharField(default=b'open', max_length=64, choices=[(b'open', b'Open'), (b'investigating', b'Investigating'), (b'reopen', b'Re-open'), (b'resolved', b'Resolved')]),
        ),
    ]
