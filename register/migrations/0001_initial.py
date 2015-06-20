# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations

def check_and_add_column(apps, schema_editor):
    import sqlite3
    conn = sqlite3.connect('db7.sqlite3')
    cur = conn.cursor()
    result = [True for i in cur.execute('PRAGMA table_info(auth_group)') if i[1] == 'is_auto_assign']

    if not result:
        cur.execute('ALTER TABLE auth_group ADD COLUMN is_auto_assign BOOLEAN DEFAULT FALSE')




class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(check_and_add_column,),

        # If you need to run SQL directly from here
        # migrations.RunSQL("ALTER TABLE auth_group ADD COLUMN is_auto_assign BOOLEAN DEFAULT FALSE"),
    ]




