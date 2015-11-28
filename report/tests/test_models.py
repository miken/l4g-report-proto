import os
import time
from django.test import TestCase
from sm_api import SurveyMonkeyClient
from report.models import Survey, Question, Choice, Respondent, Answer


class SurveyTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        # Read SurveyMonkey API Token & Key
        SURVEYMONKEY_API_TOKEN = os.environ.get('SURVEYMONKEY_API_TOKEN')
        SURVEYMONKEY_API_KEY = os.environ.get('SURVEYMONKEY_API_KEY')
        self.client = SurveyMonkeyClient(SURVEYMONKEY_API_TOKEN, SURVEYMONKEY_API_KEY)
        # Create a survey and connect to SurveyMonkey via client
        self.survey = Survey.objects.create(name="Mike Test - DO NOT USE")

    def tearDown(self):
        # Cool down 1 second to comply with SurveyMonkey API
        time.sleep(1)

    def test_update_details_for_nonexistent_survey(self):
        fake_survey = Survey.objects.create(name="Does not exist")
        fake_survey.update_details()
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Choice.objects.count(), 0)

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
        # Comment question should be tagged as open_ended
        comment_qn = Question.objects.get(text="Enter a comment here")
        self.assertTrue(comment_qn.open_ended)
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
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Choice.objects.count(), 0)
        # No new questions are created after the first update call
        self.survey.update_details()
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Choice.objects.count(), 11)
        # Wait for 1 second before making the second call to comply with API
        time.sleep(1)
        self.survey.update_details()
        self.assertEqual(Question.objects.count(), 4)
        self.assertEqual(Choice.objects.count(), 11)

    def test_download_responses(self):
        self.assertEqual(Respondent.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)
        self.survey.update_details()
        self.survey.download_responses()
        respondent_list = Respondent.objects.values_list("sm_id", flat=True).order_by("sm_id")
        respondent_list = list(respondent_list)
        expected = [u'4352785923', u'4352786417', u'4352786821', u'4352787305', u'4352787778']
        self.assertEqual(respondent_list, expected)
        # Pick a respondent and check nesting of Question & Choice
        respondent = Respondent.objects.get(sm_id=u'4352787778')
        answer_list = respondent.answer_set.values_list("question__text", "choice__text").order_by("question__text", "choice__text")
        answer_list = list(answer_list)
        expected = [
            # Enter a comment here is null because open-ended question does not have choice
            # The comment is stored in answer.text, which we will test after
            (u'Enter a comment here', None),
            (u'Select-all question', u'Option 1'),
            (u'Select-all question', u'Option 2'),
            (u'Select-all question', u'Option 3'),
            (u'Select-one question', u'Option 3'),
            (u'This is a select-one question with weighting', u'Option 4')
        ]
        self.assertEqual(answer_list, expected)
        # Check open-ended
        another_respondent = Respondent.objects.get(sm_id=u'4352786821')
        all_comments = another_respondent.answer_set.values_list("text", flat=True)
        comment = [c for c in all_comments if c is not None][0]
        self.assertEqual(comment, u'Survey taker 3')

    def test_download_responses_twice(self):
        self.assertEqual(Respondent.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)
        # No new respondents/answers are created after the first download call
        self.survey.update_details()
        self.survey.download_responses()
        self.assertEqual(Respondent.objects.count(), 5)
        self.assertEqual(Answer.objects.count(), 26)
        # Wait for 1 second before making the second call to comply with API
        time.sleep(1)
        self.survey.update_details()
        self.survey.download_responses()
        self.assertEqual(Respondent.objects.count(), 5)
        self.assertEqual(Answer.objects.count(), 26)
