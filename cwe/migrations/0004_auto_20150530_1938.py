# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0003_auto_20150530_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tags',
            name='designFlaw',
        ),
        migrations.DeleteModel(
            name='DesignFlaw',
        ),
        migrations.DeleteModel(
            name='Tags',
        ),
    ]
