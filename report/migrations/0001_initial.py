# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sm_id', models.CharField(max_length=50, verbose_name=b'SurveyMonkey ID')),
                ('text', models.CharField(max_length=255)),
                ('weight', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sm_id', models.CharField(max_length=50, verbose_name=b'SurveyMonkey ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Respondent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sm_id', models.CharField(max_length=50, verbose_name=b'SurveyMonkey ID')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('sm_id', models.CharField(max_length=50, verbose_name=b'SurveyMonkey ID')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('answer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='report.Answer')),
                ('text', models.TextField()),
            ],
            bases=('report.answer',),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('answer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='report.Answer')),
                ('value', models.IntegerField()),
            ],
            bases=('report.answer',),
        ),
        migrations.AddField(
            model_name='respondent',
            name='survey',
            field=models.ForeignKey(to='report.Survey'),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(to='report.Survey'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(to='report.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='choice_id',
            field=models.ForeignKey(to='report.Choice'),
        ),
        migrations.AddField(
            model_name='answer',
            name='respondent_id',
            field=models.ForeignKey(to='report.Respondent'),
        ),
    ]
