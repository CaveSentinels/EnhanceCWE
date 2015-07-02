# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailinvitation',
            name='key',
            field=models.CharField(default='default', unique=True, max_length=64, verbose_name=b'key'),
            preserve_default=False,
        ),
    ]
