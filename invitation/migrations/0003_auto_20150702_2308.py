# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0002_emailinvitation_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailinvitation',
            old_name='email_address',
            new_name='email',
        ),
    ]
