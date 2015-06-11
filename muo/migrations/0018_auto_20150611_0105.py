# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0017_auto_20150611_0027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='muocontainer',
            name='misuse_cases',
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case',
            field=models.ForeignKey(default=1, to='muo.MisuseCase'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usecase',
            name='misuse_case',
            field=models.ForeignKey(blank=True, to='muo.MisuseCase', null=True),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='muo_container',
            field=models.ForeignKey(to='muo.MUOContainer'),
        ),
    ]
