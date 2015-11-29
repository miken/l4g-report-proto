# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_survey_error_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['survey', 'text']},
        ),
        migrations.AddField(
            model_name='question',
            name='nps',
            field=models.BooleanField(default=False),
        ),
    ]
