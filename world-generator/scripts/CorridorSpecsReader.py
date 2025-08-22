import json
import os

class CorridorSpecsReader:
    def __init__(self):
        self.filePath = os.getenv("CORRIDOR_SPECS_FILE", None)
        if (self.filePath is None):
            raise ValueError("CORRIDOR_SPECS_FILE environment variable is not set.")
        self.validCorridors = []
        self.invalidCorridors = []
        self.load()
    
    def _open(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data

    def parse_json(self, json_object):
        valid_corridors = json_object.get("valid_corridors", [])
        invalid_corridors = json_object.get("invalid_corridors", [])
        self.validCorridors = valid_corridors
        self.invalidCorridors = invalid_corridors

    def load(self):
        json_object = self._open(self.filePath)
        self.parse_json(json_object)
        return self.validCorridors, self.invalidCorridors

