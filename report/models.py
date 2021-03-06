from __future__ import division
import os
from django.db import models
from sm_api import SurveyMonkeyClient
from report.helpers import str_truncate


class Survey(models.Model):
    name = models.CharField(max_length=255)
    # SurveyMonkey ID for this survey
    # Usually obtained after first data retrieval
    # Stored as string
    sm_id = models.CharField("SurveyMonkey ID", max_length=50, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    # Error message generated during API calls
    error_message = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        ordering = ['last_updated', 'name']

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
        try:
            pages = client.get_survey_details(self.name)
        except IndexError:
            self.error_message = "Could not find survey in SurveyMonkey. Are you sure the survey name is correct?"
        else:
            # Clear error_message
            self.error_message = None
            for p in pages:
                for q in p["questions"]:
                    # Skip if it's descriptive text
                    if q["type"]["subtype"] != "descriptive_text":
                        qid = q["question_id"]
                        question, created = Question.objects.get_or_create(sm_id=qid, survey_id=self.id)
                        question.text = q["heading"]
                        question.survey_id = self.id
                        if q["type"]["family"] == u'open_ended':
                            question.open_ended = True
                        question.save()
                        # Update question choices as well
                        for a in q['answers']:
                            # Skip if no content in text
                            if a["text"]:
                                cid = a["answer_id"]
                                text = a["text"]
                                weight = a.get("weight")
                                # TODO Allow change of choice text without
                                # creating a new choice when 
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
        try:
            data = client.get_responses(self.name)
        except IndexError:
            self.error_message = "Could not find survey in SurveyMonkey. Are you sure the survey name is correct?"
        else:
            self.error_message = None
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
                        # Associate the question with the respondent if
                        # the question is not in the set yet
                        if not respondent.questions.filter(id=question.id).exists():
                            respondent.questions.add(question)
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

    def _nps_questions(self):
        return self.question_set.filter(nps=True)
    nps_questions = property(_nps_questions)

    def _nps_respondent_count(self):
        if self.nps_questions:
            count_all_respondents = 0
            for q in self.nps_questions:
                count_all_respondents += q.respondent_set.count()
            return count_all_respondents

    def _promoters_count(self):
        if self.nps_questions:
            count_all_promoters = 0
            for q in self.nps_questions:
                count_all_promoters += q.promoters_count
            return count_all_promoters
    promoters_count = property(_promoters_count)

    def _promoters_prop(self):
        if self.nps_questions:
            count_all_promoters = self._promoters_count()
            count_all_respondents = self._nps_respondent_count()
            prop = count_all_promoters / count_all_respondents
            return int(round(prop * 100))
    promoters_prop = property(_promoters_prop)

    def _passives_count(self):
        if self.nps_questions:
            count_all_passives = 0
            for q in self.nps_questions:
                count_all_passives += q.passives_count
            return count_all_passives
    passives_count = property(_passives_count)

    def _passives_prop(self):
        if self.nps_questions:
            count_all_passives = self._passives_count()
            count_all_respondents = self._nps_respondent_count()
            prop = count_all_passives / count_all_respondents
            return int(round(prop * 100))
    passives_prop = property(_passives_prop)

    def _detractors_count(self):
        if self.nps_questions:
            count_all_detractors = 0
            for q in self.nps_questions:
                count_all_detractors += q.detractors_count
            return count_all_detractors
    detractors_count = property(_detractors_count)

    def _detractors_prop(self):
        if self.nps_questions:
            count_all_detractors = self._detractors_count()
            count_all_respondents = self._nps_respondent_count()
            prop = count_all_detractors / count_all_respondents
            return int(round(prop * 100))
    detractors_prop = property(_detractors_prop)

    def _net_promoter_score(self):
        '''
        This method finds all NPS questions for the given survey
        Across different versions of NPS questions:
        - Tally up count of all promoters
        - Tally up count of all detractors
        - Tally up count of respondents
        - Calculate promoters %
        - Calculate detractors %
        - Subtract detractors % from promoters % to arrive at NPS
        See calculation method here: https://www.netpromoter.com/know/
        '''
        if self.nps_questions:
            count_all_promoters = 0
            count_all_detractors = 0
            count_all_respondents = 0
            for q in self.nps_questions:
                count_all_promoters += q.promoters_count
                count_all_detractors += q.detractors_count
                count_all_respondents += q.respondent_set.count()
            promoters_prop = count_all_promoters / count_all_respondents
            detractors_prop = count_all_detractors / count_all_respondents
            raw_score = promoters_prop - detractors_prop
            # Need to multiply by 100 and round up
            score = round(raw_score * 100)
            return int(score)
    net_promoter_score = property(_net_promoter_score)


class Question(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)
    # Whether this question takes text input (comment) as answer
    open_ended = models.BooleanField(default=False)
    # Whether this question is part of Net Promoter Score questions
    nps = models.BooleanField(default=False)

    class Meta:
        ordering = ['survey', 'text']

    def __unicode__(self):
        return str_truncate(self.text)

    def _helper_count_responses(self, range):
        '''
        Helper method that will count the number of responses
        selecting options corresponding to the list in range
        '''
        choices = self.choice_set.filter(weight__in=range)
        answers = self.answer_set.filter(choice__in=choices)
        return answers.count()

    def _nps_promoters_count(self):
        '''
        This method only applies to NPS question
        It'll return the count of promoters (those rating 9-10)
        '''
        if self.nps:
            values_range = [9, 10]
            return self._helper_count_responses(values_range)
    promoters_count = property(_nps_promoters_count)

    def _nps_detractors_count(self):
        '''
        This method only applies to NPS question
        It'll return the count of detractors (those rating 0-6)
        '''
        if self.nps:
            values_range = range(0, 7)
            return self._helper_count_responses(values_range)
    detractors_count = property(_nps_detractors_count)

    def _nps_passives_count(self):
        '''
        This method only applies to NPS question
        It'll return the count of passives (those rating 7-8)
        '''
        if self.nps:
            values_range = [7, 8]
            return self._helper_count_responses(values_range)
    passives_count = property(_nps_passives_count)


class Choice(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    text = models.CharField(max_length=255)
    weight = models.IntegerField(null=True)
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return "{choice} - {qn}".format(choice=self.text, qn=str_truncate(self.question.text))

    def _get_raw_percentage(self):
        '''
        Proportion of respondents selecting this choice
        Defined as count of selected choices over total
        number of respondents responded to the question
        '''
        numer = self.answer_set.count()
        denom = self.question.respondent_set.count()
        if denom == 0:
            return 0
        else:
            return numer / denom
    raw_percentage = property(_get_raw_percentage)


class Respondent(models.Model):
    sm_id = models.CharField("SurveyMonkey ID", max_length=50)
    survey = models.ForeignKey(Survey)
    questions = models.ManyToManyField(Question)

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
