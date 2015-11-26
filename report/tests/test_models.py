import os
from django.test import TestCase
from sm_api import SurveyMonkeyClient
from report.models import Survey, Question


class SurveyTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        # Read SurveyMonkey API Token & Key
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        self.client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        # Create a survey and connect to SurveyMonkey via client
        self.survey = Survey.objects.create(name="Mike Test - DO NOT USE")

    def test_update_details(self):
        # Check that there is no question populated yet
        self.assertEqual(Question.objects.count(), 0)
        # Start populating Questions
        self.survey.update_details()
        # Check that there are 4 new questions "downloaded"
        # from survey
        question_list = Question.objects.values_list("text", flat=True)
        question_list = list(question_list)
        question_list.sort()
        expected = [
            u'Enter a comment here',
            u'Select-all question',
            u'Select-one question',
            u'This is a select-one question with weighting',
        ]
        self.assertEqual(question_list, expected)
