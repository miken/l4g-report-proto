import os
from django.db import models
from sm_api import SurveyMonkeyClient


class Survey(models.Model):
    name = models.CharField(max_length=255)
    # SurveyMonkey ID for this survey
    # Usually obtained after first data retrieval
    # Stored as string
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)

    def __unicode__(self):
        return self.name

    def update_details(self):
        '''
        Connects to SurveyMonkey API using known credentials
        and create or update questions & choices in db based
        on details obtained from get_survey_details API call
        '''
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        pages = client.get_survey_details(self.name)
        for p in pages:
            for q in p["questions"]:
                # Skip if it's descriptive text
                if q["type"]["subtype"] != "descriptive_text":
                    qid = q["question_id"]
                    question, created = Question.objects.get_or_create(sm_id=qid, survey_id=self.id)
                    question.text = q["heading"]
                    question.survey_id = self.id
                    question.save()
                    # TODO Create question choices


class Question(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return self.text


class Choice(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    weight = models.IntegerField()
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return self.text


class Respondent(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return "Respondent ID {}".format(self.sm_id)


class Answer(models.Model):
    choice_id = models.ForeignKey(Choice)
    respondent_id = models.ForeignKey(Respondent)


class Comment(Answer):
    text = models.TextField()


class Rating(Answer):
    value = models.IntegerField()
