# JSAV exercise downloader for A+ LMS.
# Language: Python 3.5
#
# Copyright (C) 2019-2020
# * Daniel Bruzual Balzan
#     original code 2019
#     <danielbruzual.at.gmail.dot.com>
# * Artturi Tilanterä
#     object-oriented code modified for JSAV exercise submissions, 2019-2020
#     <artturi.dot.tilantera.at.iki.dot.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import csv
from enum import Enum
import json
from pathlib import Path
import requests
import sys
import time

class ExerciseDownloader:
    def __init__(self, api_url_base, api_token):
        self.api_token = api_token
        self.api_url_base = api_url_base
        self.headers = {'Content-type': 'application/json',
            'Authorization': 'Token {0}'.format(api_token)}

    def __get_exercise_data(self, exercise_id):
        """
        Retrieves metadata of the given exercise from A+ API.

        Parameters:
        exercise_id (int): identifier of the exercise in A+ API.

        Returns:
        (dict): following fields containing metadata of the exercise:
            exercise_name   : name of the exercise shown in the GUI of A+
            course_code     : course code of the exercise
            course_name     : course name of the exercise
            course_instance : course instance of the exercise, usually a year
            max_points      : maximum points of the exercise shown in A+
            max_submissions : maximum number of submissions for the exercise
            submission_url  : A+ API url for the submissions of the exercise
        """
        api_url = '{0}exercises/{1}'.format(self.api_url_base, exercise_id)
        response = requests.get(api_url, headers = self.headers)
        print("Requesting {}. Response:\n{}".format(api_url, response))
        if response.status_code != 200:
            print("Reason: {}".format(response.reason_phrase))
            if response.status_code >= 300 and response.status_code < 400:
                print("Did you set the API URL correctly?")
            elif response.status_code == 401:
                print("Did you set the API Access token correctly?")
            elif response.status_code == 404:
                print("Are the API URL and the exercise ID correct?")
            return None

        json_data = json.loads(response.content.decode('utf-8'))
        result = {}
        result['exercise_name']   = json_data['display_name']
        result['course_code']     = json_data['course']['code']
        result['course_name']     = json_data['course']['name']
        result['course_instance'] = json_data['course']['instance_name']
        result['max_points']      = json_data['max_points']
        result['max_submissions'] = json_data['max_submissions']
        result['submissions_url'] = json_data['submissions']
        return result


    def __get_submissions(self, submissions_url):
        """
        Retrieves list of exercise submissions for given URL.
        Wrapper method for __get_submissions_recursive().

        Parameters:
        submissions_url (str): A+ API URL to pointing to the first submission.

        Returns:
        (dict):
            count (int)             : number of submissions
            submissions (list(str)) : list of submissions
        """
        result = {'count':0, 'submissions':[]}
        self.__get_submissions_recursive(submissions_url, result)
        return result

    def __get_submissions_recursive(self, api_url, result):
        """
        The actual recursive implementation for retrieving list of exercise
        submissions for given api_url.

        Parameters:
        api_url (str): current A+ API URL
        result (dict): dictionary to store the data recursively
        """
        response = requests.get(api_url, headers = self.headers)
        if response.status_code == 200:
            json_data = json.loads(response.content.decode('utf-8'))
            result['submissions'].extend(json_data['results'])
            result['count'] = json_data['count']
            if json_data['next'] is not None:
                self.__get_submissions_recursive(json_data['next'], result)

    def __get_submission_data(self, submission_url):
        """
        Retrieves data of given submission_url from A+ API.

        Parameters:
        submission_url (str): URL of the submission in the A+ API.

        Returns:
        (dict):
            submission_id   (str): Unique identifier of the submission in the A+
                                  API
            jsav_points     (str): Points given by the JSAV exercise
            jsav_max_points (str): Maximum points given by the JSAV exercise
            jsav_recording  (str): JSON data containing the JSAV exercise
                                   recording
        """
        response = requests.get(submission_url, headers = self.headers)
        result = {}
        if response.status_code != 200:
            print("Error: got HTTP {} for {}".format(response.status_code,
                submission_url))
            return None

        json_data = json.loads(response.content.decode('utf-8'))
        if json_data == None:
            print("Error: invalid JSON data for {}".format(submission_url))
            return None

        result['submission_id'] = json_data['id']
        # result['username'] = json_data['submitters'][0]['username']
        # result['student_id'] = json_data['submitters'][0]['student_id']
        # result['email'] = json_data['submitters'][0]['email']
        # result['submission_time'] = json_data['submission_time']
        result['status'] = json_data['status']
        # result['late_penalty_applied'] = json_data['late_penalty_applied']
        # result['grade'] = json_data['grade']

        accepted_statuses = ['ready', 'unofficial']

        if result['status'] not in accepted_statuses:
            print("Skipping submission having id {}, because 'status' is '{}'"
                .format(result['submission_id'], result['status']))

        # print("JSON data: {}".format(json_data))

        if not 'grading_data' in json_data:
            print("Error: no 'grading_data' field in {}".format(submission_url))
            return None

        if json_data['grading_data'] is None:
            print("Error: 'grading_data' field is None in {}".format(submission_url))
            return None

        if (not 'points' in json_data['grading_data']):
            print("Error: no grading_data.points in {}".format(submission_url))
            return None

        if (not 'max_points' in json_data['grading_data']):
            print("Error: no grading_data.max_points in {}".format(submission_url))
            return None

        if (not 'grading_data' in json_data['grading_data']):
            print("Error: no grading_data.grading_data in {}".format(submission_url))
            return None

        result['jsav_points'] = json_data['grading_data']['points']
        result['jsav_max_points'] = json_data['grading_data']['max_points']
        result['jsav_recording'] = json_data['grading_data']['grading_data']
        return result

    def process_exercises(self, exercises, download_directory):
        """Processes list of JSAV exercise download requests. Downloads the
        submissions of each request into a JSON file.

        Parameters:
        exercise (list(ExerciseDL)): list containing ExerciseDL objects

        download_directory (str): main directory to download exercise data

        Writes files:
            For each x in exercises, creates file
            {download_directory}/{x['name']}/{x['year']}.json

        """
        maindir = Path(download_directory)
        if not maindir.is_dir():
            maindir.mkdir()

        for exercise_rq in exercises:
            exdir = Path(download_directory + '/' + exercise_rq.name)
            if not exdir.is_dir():
                exdir.mkdir()

            exercise = self.__get_exercise_data(exercise_rq.id)
            file_name = "{0}/{1}/{2}.json".format(download_directory,
                exercise_rq.name, exercise_rq.year)
            self.__exercise_to_file(exercise_rq, exercise, file_name)


    def __exercise_to_file(self, exercise_rq, exercise, file_name):
        """Downloads submissions of one exercise into a file.

        Parameters:
        exercise (dict)         : retrieved exercise metadata, see
                                  __get_exercise_data()
        exercise_rq (ExerciseDL): exercise download request
        file_name (str)         : path and name of the file to write

        Writes file:
        file_name

        """

        print(("----------------------------------------\n"
               "Exercise  : {}\n"
               "Metadata  : {}\n"
               "File name : {}").format(exercise_rq, exercise, file_name))

        with open(file_name, 'w') as json_file:
            submissions = self.__get_submissions(exercise['submissions_url'])

            print("Found {} submissions.".format(submissions['count']))

            metadata = json.dumps({
                'id'       : exercise_rq.id,
                'type'     : exercise_rq.name,
                'longname' : exercise_rq.longname,
                'year'     : exercise_rq.year,
                'course_code'     : exercise['course_code'],
                'course_name'     : exercise['course_name'],
                'course_instance' : exercise['course_instance'],
                'max_points'      : exercise['max_points'],
                'max_submissions' : exercise['max_submissions'],
                'submissions_url' : exercise['submissions_url']
            })
            json_file.write('{\n'
                '  "application" : "JSAV Inspector",\n'
                '  "version"     : 1,\n'
                '  "metadata"    : ' + metadata + ',\n'
                '  "submissions" : [\n')

            i = 0
            n = int(submissions['count'])
            comma = ''
            for su in submissions['submissions']:
                submission = self.__get_submission_data(su['url'])
                i += 1
                if submission == None:
                    print ('Submission {0}/{1}: skipped'.format(i,
                        submissions['count']))
                    continue
                else:
                    print ('Submission {0}/{1}: id {2}'.format(i,
                        submissions['count'], submission['submission_id']))

                json_file.write('  ' + comma + '{\n'
                '    "id" : ' + str(submission['submission_id']) + ',\n'
                '    "points" : ' + str(submission['jsav_points']) + ',\n'
                '    "max_points" : ' + str(submission['jsav_max_points']) + ',\n'
                '    "recording" : ' + submission['jsav_recording'] + '\n}')
                #'    "recording" : {}\n  }\n')
                if (comma == ''):
                    comma = ','

                if (i == n):
                    break

                # A+ might block if this program generates too many requests in
                # too short a time. Therefore sleep().
                time.sleep(0.5)
                #print ('Submission {0}/{1}'.format(i, submissions['count']), end='\r')

            json_file.write("]\n}\n")

            print("\nDone.\n")

# JSAV exercise types supported by Artturi's JSAV Inspector.
class JSAVType(Enum):
    # short id = "Long name"
    buildheap = "Heap build"
    quicksort = "Quicksort"
    dijkstra = "Dijkstra's algorithm"

class ExerciseDL:

    def __init__(self, id, name, year):
        """Creates a representation for a JSAV exercise whose submissions need
        to be downloaded.

        Parameters:
        id (int): identifier of the exercise in A+
        name (JSAVType): short name of the exercise
        year (int): year of the course instance

        Parameter 'id' must be obtained manually by browsing the A+ API.
        Parameter 'year' can be chosen freely, but it cannot be nonempty.
        """
        if not isinstance(name, JSAVType):
            raise TypeError("Parameter 'name' should be JSAVType")

        self.id = id
        self.name = name.name
        self.longname = name.value
        self.year = year

    def __str__(self):
        return "<id: {}, type: {}, year: {}>".format(self.id, self.name,
            self.year)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

print("A+ JSAV submission downloader ")
if len(sys.argv) != 2:
    print("Usage: {} <A+ API Access Token>".format(sys.argv[0]))
    print("See https://plus.cs.aalto.fi/accounts/accounts/")

else:
    api_url_base = 'https://plus.cs.aalto.fi/api/v2/'
    api_token = sys.argv[1]
    exercises = [
        # Hardcoded exercise identifiers. These must read manually from the
        # A+ api and then copypasted here.
        #ExerciseDL(18883, JSAVType.buildheap, 2018),
        #ExerciseDL(18857, JSAVType.quicksort, 2018),
        #ExerciseDL(18938, JSAVType.dijkstra, 2018)
        # ExerciseDL(13212, JSAVType.buildheap, 2017),
        # ExerciseDL(14333, JSAVType.quicksort, 2017),
        # ExerciseDL(13263, JSAVType.dijkstra, 2017),
        # ExerciseDL(6198, JSAVType.buildheap, 2016),
        # ExerciseDL(11700, JSAVType.quicksort, 2017),
        # ExerciseDL(6636, JSAVType.dijkstra, 2017)
        ExerciseDL(22488, JSAVType.buildheap, 2019),
        ExerciseDL(22674, JSAVType.buildheap, '2019-en')
    ]
    download_directory = 'data'

    edl = ExerciseDownloader(api_url_base, api_token)
    edl.process_exercises(exercises, download_directory)
