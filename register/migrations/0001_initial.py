# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, connection

def check_and_add_assign_column(apps, schema_editor):
    cursor = connection.cursor()

    # check if column exist before adding column
    cursor.execute("select * from auth_group limit 1")
    if not [col for col in cursor.description if col[0] == 'is_auto_assign']:
        cursor.execute('ALTER TABLE auth_group ADD COLUMN is_auto_assign BOOLEAN DEFAULT FALSE')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(check_and_add_assign_column,),
    ]




