# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0013_auto_20150610_0021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='osr',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='osr',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='osr',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='osr',
            name='use_case',
        ),
        migrations.RemoveField(
            model_name='muocontainer',
            name='osrs',
        ),
        migrations.RemoveField(
            model_name='muocontainer',
            name='use_cases',
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='new_misuse_case',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='muo_container',
            field=models.ForeignKey(related_name='use_cases', on_delete=b'Cascade', default=1, to='muo.MUOContainer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usecase',
            name='osr',
            field=models.TextField(default='abc'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='muocontainer',
            name='misuse_cases',
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_cases',
            field=models.ForeignKey(related_name='muo_container', on_delete=b'Cascade', default=1, to='muo.MisuseCase'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='OSR',
        ),
    ]
