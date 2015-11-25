import os
from django.test import TestCase
from sm_api import SurveyMonkeyClient


class SMClientTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        # Read SurveyMonkey API Token & Key
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        self.api_client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        # Create a survey and connect to SurveyMonkey via client
        self.survey_name = "Mike Test - DO NOT USE"

    def test_get_survey_list(self):
        '''
        Test that the client will return a list of dict
        containing survey IDs matching Mike Test - DO NOT USE
        '''
        survey_list = self.api_client.get_survey_list(self.survey_name)
        expected = [{u'survey_id': u'72140246'}]
        self.assertEqual(survey_list, expected)
