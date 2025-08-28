import json
import os

class RampSpecsReader:
    def __init__(self):
        self.filePath = os.getenv("RAMP_SPECS_FILE", None)
        if (self.filePath is None):
            raise ValueError("RAMP_SPECS_FILE environment variable is not set.")
        self.validRamps = []
        self.invalidRamps = []
        self.load()
    
    def _open(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data

    def parse_json(self, json_object):
        valid_ramps = json_object.get("valid_ramps", [])
        invalid_ramps = json_object.get("invalid_ramps", [])
        self.validRamps = valid_ramps
        self.invalidRamps = invalid_ramps

    def load(self):
        json_object = self._open(self.filePath)
        self.parse_json(json_object)
        return self.validRamps, self.invalidRamps

