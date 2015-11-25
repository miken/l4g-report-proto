import os
from django.test import TestCase
from sm_api import SurveyMonkeyClient
from report.models import Survey


class SurveyTestCase(TestCase):
    def setUp(self):
        # Read SurveyMonkey API Token & Key
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        self.client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        # Create a survey and connect to SurveyMonkey via client

    def test_dummy(self):
        self.assertEqual(1, 1)
