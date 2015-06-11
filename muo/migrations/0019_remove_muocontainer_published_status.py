# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0018_auto_20150611_0105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='muocontainer',
            name='published_status',
        ),
    ]
