# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20151125_1817'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='answer_ptr',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='answer_ptr',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.AddField(
            model_name='answer',
            name='text',
            field=models.TextField(null=True),
        ),
    ]
