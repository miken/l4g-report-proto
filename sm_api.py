import requests
import json
from unicodecsv import DictWriter


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


class Survey(object):
    '''
    This is an object wrapper for a survey
    in SurveyMonkey API
    Need to instantiate a SurveyMonkeyClient first
    to work with the survey
    '''
    def __init__(self, name, client):
        '''
        name (string): Not necessarily full exact name of the survey in SurveyMonkey
            but the survey name in SM must contain this string
        client (SurveyMonkeyClient instance): Must be instantiated
            with a valid token & API key
        '''
        self.name = name
        self.client = client
        # These attributes are only available with a successful
        # connection to SurveyMonkey API endpoints
        self.question_map = self.create_question_map()
        self.question_list = self.create_question_list()
        self.raw_data = self.client.get_responses(self.name)

    def create_question_map(self):
        '''
        This method calls get_survey_details() method from SM client instance
        then extract information from pages of questions in the following
        dict data structure:
            question_id:
                answers: [
                    answer_id:
                    text:
                    weight:
                ]
                text: "..."
        '''
        pages = self.client.get_survey_details(self.name)
        question_map = {}
        for p in pages:
            for q in p["questions"]:
                # Skip if it's descriptive text
                if q["type"]["subtype"] != "descriptive_text":
                    question_id = q["question_id"]
                    question_text = q["heading"]
                    answers = []
                    for a in q['answers']:
                        ans = {
                            "answer_id": a["answer_id"],
                            "text": a["text"]
                        }
                        if "weight" in a.keys():
                            ans["weight"] = a["weight"]
                        answers.append(ans)

                    q_props = {
                        "answers": answers,
                        "text": question_text
                    }
                    question_map[question_id] = q_props
        return question_map

    def create_question_list(self):
        questions = [q["text"] for q in self.question_map.itervalues()]
        questions.sort()
        return questions

    def export_csv(self, filename):
        '''
        Export raw_data to CSV format with given filename string
        Each row represents a response
        Each column represents a question
        '''
        with open(filename, "w") as csvfile:
            fieldnames = ["Respondent_ID"]
            fieldnames.extend(self.question_list)
            writer = DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for r in self.raw_data:
                # Create a row dict for the writer
                row = {}
                row["Respondent_ID"] = r["respondent_id"]
                # Next, map question ID with the answer
                for q in r["questions"]:
                    # In each dict q there are 2 keys: "answers", and "question_id"
                    # First, use "question_id" to locate the question text
                    question_id = q["question_id"]
                    question_text = self.question_map[question_id]["text"]
                    options = self.question_map[question_id]["answers"]
                    # Next, find the response for this question
                    # q["answers"] is a list of dicts
                    # TODO If q["answers"] has more than one element,
                    # It's a select-all question, need to build out one column
                    # per option choice
                    # For now, only use the first element in q["answers"]
                    raw_answer = q["answers"][0]
                    # Here's the tricky part, in the raw_answer dict
                    # Sometimes results come with "col", "row", or "text"
                    # If "text" exists, that's a dead giveaway that it's an open-ended question
                    # We can save that as answer
                    if "text" in raw_answer.keys():
                        answer = raw_answer["text"]
                    else:
                        # A qualitative response
                        # There will be "row" and "col"
                        # Use these to look up for responses
                        row_id = raw_answer.get("row")
                        col_id = raw_answer.get("col")
                        # If col_ans exists, it's a horizontal question
                        # With weight assigned to it, find the "weight" value
                        # from question_map and assign to answer
                        if col_id:
                            option = [o for o in options if o["answer_id"] == col_id][0]
                            try:
                                answer = option["weight"]
                            except KeyError:
                                print "Cannot find `weight` in option {}".format(option)
                                answer = "ERROR"
                        else:
                            # Try looking up with row_id
                            option = [o for o in options if o["answer_id"] == row_id][0]
                            # Assign text value to the answer
                            answer = option["text"]
                    # Dummy code for now
                    row[question_text] = answer
                # Write the row
                writer.writerow(row)