# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0015_auto_20150610_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usecase',
            name='misuse_case',
            field=models.ForeignKey(to='muo.MisuseCase', on_delete=b'Cascade'),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='muo_container',
            field=models.ForeignKey(to='muo.MUOContainer', on_delete=b'Cascade'),
        ),
    ]
