import json


class Local_Storage:
    def __init__(self, directory: str):
        self.dir = directory
    
    def save(self, filename: str, data: dict):
        with open(self.dir + filename, 'w') as f:
            json.dump(data, f)
    
    def load(self, filename: str) -> dict:
        with open(self.dir + filename, 'r') as f:
            return json.load(f)