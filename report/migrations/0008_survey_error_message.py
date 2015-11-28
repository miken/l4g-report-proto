# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_auto_20151127_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='error_message',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
