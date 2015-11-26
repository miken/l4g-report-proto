import os
from django.db import models
from django.utils import timezone
from sm_api import SurveyMonkeyClient
from report.helpers import str_truncate


class Survey(models.Model):
    name = models.CharField(max_length=255)
    # SurveyMonkey ID for this survey
    # Usually obtained after first data retrieval
    # Stored as string
    sm_id = models.CharField("SurveyMonkey ID", max_length=50, null=True)
    last_updated = models.DateTimeField(auto_now=True)

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
                    # Update question choices as well
                    for a in q['answers']:
                        # Skip if no content in text
                        if a["text"]:
                            cid = a["answer_id"]
                            text = a["text"]
                            weight = a.get("weight")
                            choice, created = Choice.objects.get_or_create(
                                sm_id=cid,
                                text=text,
                                weight=weight,
                                question_id=question.id
                                )

    def download_responses(self):
        '''
        Use get_responses() method in SurveyMonkeyClient to
        retrieve a list of response dicts, then get_or_create
        Respondent and Answer associated with the survey

        You should always call update_details() before download_responses()
        to avoid having non-existent Questions for survey that has never
        been updated previously
        '''
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        data = client.get_responses(self.name)
        for r in data:
            rid = r["respondent_id"]
            respondent, created = Respondent.objects.get_or_create(sm_id=rid, survey_id=self.id)
            # Only update Answer/Comment/Rating if it's a new respondent
            # TODO This means that if a respondent somehow update
            # their answers after submission, the updated value will not be reflected
            # unless we create a manual override here
            if created:
                for q in r["questions"]:
                    # In each dict q there are 2 keys: "answers", and "question_id"
                    # First, use "question_id" to locate the question text
                    qid = q["question_id"]
                    question = self.question_set.get(sm_id=qid, survey_id=self.id)
                    # Next, find the response for this question
                    # q["answers"] is a list of dicts
                    for raw_answer in q["answers"]:
                        # Here's the tricky part, in the raw_answer dict
                        # Sometimes results come with "col", "row", or "text"
                        # If "text" exists, that's a dead giveaway that it's an open-ended question
                        # We can save that as comment
                        if "text" in raw_answer.keys():
                            comment, created = Answer.objects.get_or_create(
                                question_id=question.id,
                                respondent_id=respondent.id,
                                text=raw_answer["text"]
                                )
                        else:
                            # A quant response
                            # There will be "row" and "col"
                            # Use these to look up for responses
                            row_id = raw_answer.get("row")
                            col_id = raw_answer.get("col")
                            # If col_ans exists, it's a horizontal question
                            if col_id:
                                choice = question.choice_set.get(sm_id=col_id)
                            else:
                                # Try looking up with row_id
                                choice = question.choice_set.get(sm_id=row_id)
                            rating, created = Answer.objects.get_or_create(
                                question_id=question.id,
                                choice_id=choice.id,
                                respondent_id=respondent.id,
                                )

    def respondent_count(self):
        return self.respondent_set.count()

    def question_count(self):
        return self.question_set.count()


class Question(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return str_truncate(self.text)


class Choice(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return "{choice} - {qn}".format(choice=self.text, qn=str_truncate(self.question.text))


class Respondent(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return "ID {}".format(self.sm_id)


class Answer(models.Model):
    question = models.ForeignKey(Question)
    # Not all questions have choices, e.g., open-ended
    choice = models.ForeignKey(Choice, null=True)
    respondent = models.ForeignKey(Respondent)
    # Input for open-ended
    text = models.TextField(null=True)

    def __unicode__(self):
        q = str_truncate(self.question.text)
        if self.text:
            a = str_truncate(self.text)
            string = '"{a}" - {q}'
        else:
            a = str_truncate(self.choice.text)
            string = '{a} - {q}'
        return string.format(a=a, q=q)
