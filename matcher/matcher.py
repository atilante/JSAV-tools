# Misconception matcher

import csv
import json
import math
import time
from buildheap import BuildHeapMatcher

class MisconceptionMatcher:

    def __init__(self):
        # Exercise recording
        self.exercise = None
        self.supportedTypes = ['buildheap', 'dijkstra', 'quicksort']
        self.buildheap = BuildHeapMatcher()

    def check_field(self, data, key, value):
        """Verifies that given data is a dict with given key-value pair

        Parameters:
        data (dict): dictionary-type data to be checked
        key        : key to be searched for
        value      : value(s) that must match the given key.
                     If value is a list, it is enough that data[key] matches to
                     one entry in value.
        """
        if not key in data:
            raise Exception("Field '{}' not found!".format(key))
        if isinstance(value, list):
            if data[key] not in value:
                raise Exception("Field '{}' was '{}', should be one of {}."
                    .format(key, data[key], value))
        else:
            if data[key] != value:
                raise Exception("Field '{}' was '{}', should be '{}'!".format(key,
                    data[key],value))

    def load_file(self, file_name):
        """Loads a JSAV inspector file"""
        print("Opening file {}".format(file_name))
        json_data = {}
        with open(file_name) as json_file:
            json_data = json.load(json_file)

        submission_count = 0
        try:
            self.check_field(json_data, 'application', 'JSAV Inspector')
            self.check_field(json_data, 'version', 1)
            self.check_field(json_data['metadata'], 'type', self.supportedTypes)
            submission_count = len(json_data['submissions'])
        except Exception as ex:
            print("Could not load data: {}".format(ex))
            return

        self.exercise = json_data
        self.exercise['submission_by_id'] = dict()
        for s in self.exercise['submissions']:
            self.exercise['submission_by_id'][s['id']] = s
        
        meta = json_data['metadata']
        print("Course:\n  Code: {}\n  Name: {}\n  Year: {}".format(
            meta['course_code'],
            meta['course_name'],
            meta['course_instance']))
        print("Exercise: {} ({})".format(meta['longname'], meta['type']))
        print("{} submissions".format(submission_count))
        print("----------- file loaded successfully")
            
    def append_file(self, file_name):
        """Append a JSAV inspector file to already loaded data"""
        print("Opening file {} to append in previous data".format(file_name))
        
        json_data = {}
        with open(file_name) as json_file:
            json_data = json.load(json_file)

        submission_count = 0
        try:
            self.check_field(json_data, 'application', 'JSAV Inspector')
            self.check_field(json_data, 'version', 1)
            self.check_field(json_data['metadata'], 'type', self.supportedTypes)
            submission_count = len(json_data['submissions'])
        except Exception as ex:
            print("Could not load data: {}".format(ex))
            return
        
        expected_type = self.exercise['metadata']['type']
        found_type = json_data['metadata']['type']
        if found_type != expected_type:
            raise Exception(("The exercise type of earlier file was {}, "
                "but current file has type {}").format(expected_type,
                                                       found_type))
            
        if self.exercise['metadata'] == json_data['metadata']:
            raise Exception("File already loaded!")
        
        for s in json_data['submissions']:
            self.exercise['submission_by_id'][s['id']] = s
        
        meta = json_data['metadata']
        print("Course:\n  Code: {}\n  Name: {}\n  Year: {}".format(
            meta['course_code'],
            meta['course_name'],
            meta['course_instance']))
        print("Exercise: {} ({})".format(meta['longname'], meta['type']))
        print("{} submissions".format(submission_count))
        
        self.exercise['submissions'] += json_data['submissions']
        print("----------- file loaded successfully")
        
    def load_manual_classification(self, file_name):
        """Appends manual classification to already loaded JSAV inspector data.
        The file must be a CSV (comma-separated value) file. Example:
        
        year,id,manual_class
        2016,549368,0
        2016,549375,100
        ...
        """
        
        i = 0
        with open(file_name, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                id = int(row['id'])
                subm = self.exercise['submission_by_id'][id]
                subm['manual_class'] = int(row['manual_class'])                
        
    def print_csv(self):
        """Prints data of a JSAV inspector file in CSV format"""
        print("No,Id,JSAV-score%")
        i = 1
        for s in self.exercise['submissions']:
            score_percent = math.floor(100 * float(s['points']) /
                float(s['max_points']))
            print("{},{},{}".format(i, s['id'], score_percent))
            i += 1

    def match_submissions(self, matching_options, print_classes):
        """Matches loaded exercise submissions to misconceptions.
        
        Parameters:
        matching_options: depends on exercise type
        print_classes: if True, prints exercise id and class code for each
                       submission.
        """
        
        t = self.exercise['metadata']['type']
        
        N = len(self.exercise['submissions'])
        classes = [-1] * N
        debug_text = [] # will contain a debug string for each submission
        correct = 0
        t1 = time.perf_counter()
        if t == 'buildheap':
            for i in range(N):
                s = self.exercise['submissions'][i]                
                cls = self.buildheap.match(s['recording'], matching_options,
                    debug_text)
                if 'manual_class' in s and cls == s['manual_class']:
                    correct += 1
                classes[i] = cls
        classification_time = time.perf_counter() - t1
        
        if (print_classes):
            print("id best_class debug")
            for i in range(N):
                s = self.exercise['submissions'][i]
                print("{} {} {}".format(s['id'], classes[i], debug_text[i]))
                
        if (correct > 0):
            accuracy = correct / N
            print("Classification accuracy: {0:2.3f}".format(accuracy))


if __name__ == "__main__":
    matcher = MisconceptionMatcher()
    #matcher.buildheap.describe_variants()
    matcher.load_file('../data/buildheap/2016.json')
    matcher.append_file('../data/buildheap/2018.json')
    matcher.load_manual_classification('../data/buildheap/manual.csv')
    
    options = [
#         {'similarity': 'states', 'Jaccard': False, 'threshold': 3},
#         {'similarity': 'lcs', 'Jaccard': False, 'threshold': 2},
#         {'similarity': 'states', 'Jaccard': True, 'threshold': 0.6},        
#         {'similarity': 'lcs', 'Jaccard': True, 'threshold': 0.8},
#           {'similarity': 'states', 'Jaccard': False, 'threshold': 3,
#            'verbosity' : 1}        
          {'similarity': 'lcs', 'Jaccard': True, 'threshold': 0.8,
           'verbosity' : 1}        
        ]
    print_classes = True
    
    for opt in options:
        #print(opt)
        matcher.match_submissions(opt, print_classes)
