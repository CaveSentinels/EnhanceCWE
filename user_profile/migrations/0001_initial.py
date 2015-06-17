# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MUONotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notify_when_muo_accepted', models.BooleanField(default=False)),
                ('notify_when_muo_rejected', models.BooleanField(default=False)),
                ('notify_when_muo_voted_up', models.BooleanField(default=False)),
                ('notify_when_muo_voted_down', models.BooleanField(default=False)),
                ('notify_when_muo_commented', models.BooleanField(default=False)),
                ('notify_when_muo_duplicate', models.BooleanField(default=False)),
                ('notify_when_muo_inappropriate', models.BooleanField(default=False)),
                ('notify_when_muo_submitted_for_review', models.BooleanField(default=False)),
                ('notify_when_custom_muo_created', models.BooleanField(default=False)),
                ('notify_when_custom_muo_promoted_as_generic', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
