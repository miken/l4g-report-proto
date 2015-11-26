# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0004_auto_20151125_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 26, 21, 32, 9, 780122, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
