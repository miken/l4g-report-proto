import os
import time
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

    def tearDown(self):
        # Add a second wait in between each test
        # To prevent running over API quota
        time.sleep(1)

    def test_get_survey_list(self):
        '''
        Test that the client will return a list of dict
        containing survey IDs matching Mike Test - DO NOT USE
        '''
        survey_list = self.api_client.get_survey_list(self.survey_name)
        expected = [{u'survey_id': u'72140246'}]
        self.assertEqual(survey_list, expected)

    def test_get_survey_id(self):
        '''
        The client should return only one single ID
        for Mike Test - DO NOT USE
        '''
        survey_id = self.api_client.get_survey_id(self.survey_name)
        self.assertEqual(survey_id, u'72140246')

    def test_get_survey_details(self):
        survey_pages = self.api_client.get_survey_details(self.survey_name)
        # survey_pages is a list
        self.assertTrue(isinstance(survey_pages, list))
        # There is only 1 element/page
        self.assertEqual(len(survey_pages), 1)
        # Check each element of pages to make sure they contain the correct keys
        expected_page_keys = [u'position', u'sub_heading', u'page_id', u'heading', u'questions']
        for p in survey_pages:
            self.assertEqual(p.keys(), expected_page_keys)

    def test_get_respondent_list(self):
        respondent_ids = self.api_client.get_respondent_list(self.survey_name)
        expected = [u'4352787778', u'4352787305', u'4352786821', u'4352786417', u'4352785923']
        self.assertEqual(respondent_ids, expected)

    def test_get_responses(self):
        responses = self.api_client.get_responses(self.survey_name)
        # Check Respondent IDs
        respondent_ids = [r['respondent_id'] for r in responses]
        expected_resp_ids = [u'4352787778', u'4352787305', u'4352786821', u'4352786417', u'4352785923']
        self.assertEqual(respondent_ids, expected_resp_ids)
