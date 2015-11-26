# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='weight',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='sm_id',
            field=models.CharField(max_length=50, null=True, verbose_name=b'SurveyMonkey ID'),
        ),
    ]
