# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0019_remove_muocontainer_published_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muocontainer',
            name='misuse_case',
            field=models.ForeignKey(to='muo.MisuseCase', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
