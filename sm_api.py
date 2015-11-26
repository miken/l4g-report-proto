import requests
import json


class SurveyMonkeyClient(object):
    HOST = "https://api.surveymonkey.net"

    def __init__(self, token, api_key):
        self.token = token
        self.api_key = api_key
        client = requests.session()
        client.headers = {
            "Authorization": "bearer {}".format(self.token),
            "Content-Type": "application/json"
        }
        client.params = {
            "api_key": api_key
        }
        self.client = client

    def post_request(self, endpoint, data):
        '''
        Helper method that handles POST request
        taking an endpoint string to add to the URI
        and data dict
        Returns a dict
        '''
        uri = "%s%s" % (self.HOST, endpoint)
        response = self.client.post(uri, data=json.dumps(data))
        response_json = response.json()
        return response_json

    def get_survey_list(self, survey_name):
        '''
        This method makes a POST request to SurveyMonkey
        using get_survey_list endpoint and returns a list
        of dict containing survey IDs matching the string
        survey_name, e.g.,
            [{u'survey_id': u'71175037'}]
        '''
        SURVEY_LIST_ENDPOINT = "/v2/surveys/get_survey_list"
        data = {"title": survey_name}
        response_dict = self.post_request(SURVEY_LIST_ENDPOINT, data)
        survey_list = response_dict["data"]["surveys"]
        return survey_list

    def get_survey_id(self, survey_name):
        '''
        Helper method that call get_survey_list() method
        to get a list of survey IDs matching survey_name
        then return the first element in the list
        '''
        survey_list = self.get_survey_list(survey_name)
        survey_id = survey_list[0]["survey_id"]
        return survey_id

    def get_survey_details(self, survey_name):
        '''
        This method makes a POST request to SurveyMonkey
        using get_survey_details endpoint and returns a list
        containing pages of questions
        '''
        SURVEY_DETAILS_ENDPOINT = "/v2/surveys/get_survey_details"
        data = {"survey_id": self.get_survey_id(survey_name)}
        response_dict = self.post_request(SURVEY_DETAILS_ENDPOINT, data)
        pages = response_dict["data"]["pages"]
        return pages

    def get_respondent_list(self, survey_name):
        '''
        This method makes a POST request to SurveyMonkey
        using get_response_list endpoint and returns a list
        Respondent ID for a given survey
        '''
        RESPONDENT_LIST_ENDPOINT = "/v2/surveys/get_respondent_list"
        data = {"survey_id": self.get_survey_id(survey_name)}
        response_dict = self.post_request(RESPONDENT_LIST_ENDPOINT, data)
        response_ids = [r["respondent_id"] for r in response_dict["data"]["respondents"]]
        return response_ids

    def get_responses(self, survey_name):
        '''
        This method makes a POST request to SurveyMonkey
        using get_responses endpoint and returns a list
        nested response dict for a given survey
        '''
        RESPONSES_ENDPOINT = "/v2/surveys/get_responses"
        data = {
            "survey_id": self.get_survey_id(survey_name),
            "respondent_ids": self.get_respondent_list(survey_name),
        }
        response_dict = self.post_request(RESPONSES_ENDPOINT, data)
        return response_dict["data"]
