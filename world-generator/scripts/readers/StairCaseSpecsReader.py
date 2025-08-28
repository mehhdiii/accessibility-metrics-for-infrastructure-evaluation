import json
import os

class StairCaseSpecsReader:
    def __init__(self):
        self.filePath = os.getenv("STAIRCASE_SPECS_FILE", None)
        if (self.filePath is None):
            raise ValueError("STAIRCASE_SPECS_FILE environment variable is not set.")
        self.validStairCases = []
        self.invalidStairCases = []
        self.load()
    
    def _open(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data

    def parse_json(self, json_object):
        valid_staircases = json_object.get("valid_staircases", [])
        invalid_staircases = json_object.get("invalid_staircases", [])
        self.validStairCases = valid_staircases
        self.invalidStairCases = invalid_staircases

    def load(self):
        json_object = self._open(self.filePath)
        self.parse_json(json_object)
        return self.validStairCases, self.invalidStairCases

