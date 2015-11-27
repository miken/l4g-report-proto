# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0005_survey_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='open_ended',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
