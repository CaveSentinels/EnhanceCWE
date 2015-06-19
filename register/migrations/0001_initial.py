# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("ALTER TABLE auth_group ADD COLUMN is_auto_assign BOOLEAN DEFAULT FALSE"),
    ]
