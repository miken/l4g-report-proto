from django.db import models


class Survey(models.Model):
    name = models.CharField(max_length=255)
    # SurveyMonkey ID for this survey
    # Usually obtained after first data retrieval
    # Stored as string
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)


class Question(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)


class Choice(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    weight = models.IntegerField()
    question = models.ForeignKey(Question)


class Respondent(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    survey = models.ForeignKey(Survey)


class Answer(models.Model):
    choice_id = models.ForeignKey(Choice)
    respondent_id = models.ForeignKey(Respondent)


class Comment(Answer):
    text = models.TextField()


class Rating(Answer):
    value = models.IntegerField()
