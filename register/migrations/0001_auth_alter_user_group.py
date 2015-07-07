# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations

TARGET_APP = 'auth'

class Migration(migrations.Migration):
    """
    Overriding constructor to use 'auth' instead of current app
    """
    def __init__(self, name, app_label):
        super(Migration, self).__init__(name, TARGET_APP)


    dependencies = [
        ('auth', '0005_alter_user_last_login_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_auto_assign',
            field=models.BooleanField(default=False, verbose_name='Auto Assign'),
        ),

        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
    ]