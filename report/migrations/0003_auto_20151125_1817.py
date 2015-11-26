# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_auto_20151125_1749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='respondent_id',
            new_name='respondent',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='choice_id',
        ),
        migrations.AddField(
            model_name='answer',
            name='choice',
            field=models.ForeignKey(to='report.Choice', null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(default=None, to='report.Question'),
            preserve_default=False,
        ),
    ]
