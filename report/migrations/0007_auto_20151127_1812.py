# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0006_question_open_ended'),
    ]

    operations = [
        migrations.AddField(
            model_name='respondent',
            name='questions',
            field=models.ManyToManyField(to='report.Question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='open_ended',
            field=models.BooleanField(default=False),
        ),
    ]
