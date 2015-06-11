# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0014_auto_20150610_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muocontainer',
            name='new_misuse_case',
            field=models.TextField(null=True, blank=True),
        ),
    ]
