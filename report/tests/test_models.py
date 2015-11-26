import os
from django.test import TestCase
from sm_api import SurveyMonkeyClient
from report.models import Survey, Question, Choice


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
        self.assertEqual(Choice.objects.count(), 0)
        # Start populating Questions
        self.survey.update_details()
        # Check that there are 4 new questions "downloaded"
        # from survey
        question_list = Question.objects.values_list("text", flat=True).order_by("text")
        question_list = list(question_list)
        expected = [
            u'Enter a comment here',
            u'Select-all question',
            u'Select-one question',
            u'This is a select-one question with weighting',
        ]
        self.assertEqual(question_list, expected)
        # Next check nesting between question and choices
        # Select-one question
        select_one = Question.objects.get(text="Select-one question")
        select_one_choices = select_one.choice_set.values_list("text", flat=True).order_by("text")
        select_one_choices = list(select_one_choices)
        expected = [
            "Option 1",
            "Option 2",
            "Option 3",
        ]
        self.assertEqual(select_one_choices, expected)
        # Select-all question
        select_all = Question.objects.get(text="Select-all question")
        select_all_choices = select_all.choice_set.values_list("text", flat=True).order_by("text")
        select_all_choices = list(select_all_choices)
        self.assertEqual(select_all_choices, expected)
        # Select-one question with weighting
        select_one_weight = Question.objects.get(text="This is a select-one question with weighting")
        select_one_weight_choices = select_one_weight.choice_set.values_list("text", "weight").order_by("weight")
        select_one_weight_choices = list(select_one_weight_choices)
        expected = [
            (u'Option 1', 1),
            (u'Option 2', 2),
            (u'Option 3', 3),
            (u'Option 4', 4),
            (u'Not available', 77),
        ]
        self.assertEqual(select_one_weight_choices, expected)

    def test_update_details_twice(self):
        # No new questions are created after the first update call
        self.survey.update_details()
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Choice.objects.count(), 11)
        self.survey.update_details()
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Choice.objects.count(), 11)
