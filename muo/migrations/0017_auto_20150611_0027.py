# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0016_auto_20150610_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muocontainer',
            name='misuse_cases',
            field=models.ForeignKey(related_name='muo_container', to='muo.MisuseCase'),
        ),
    ]
