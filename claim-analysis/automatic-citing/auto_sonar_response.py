from sonar_response import run_perplexity
import json
import time
import os

INPUT_FILE = "./claim-analysis/automatic-citing/sample.json"

class ExtractedProcessor:
    def __init__(self, input_file):
        self.input_file = input_file 
        self.latest_segment_id = 0 #needs to be global
        self.latest_modified = os.path.getmtime(input_file)

    def check_for_change(self):
        current_modified = os.path.getmtime(self.input_file)
        print("LATEST", self.latest_modified, "CURRENT", current_modified)

        if self.latest_modified < current_modified:
            self.latest_modified = current_modified
            return True
        return False

    def process(self):
        claims_found = []
        with open(self.input_file, 'r') as file:
            segment_data = json.load(file)
            for obj in segment_data:
                 # TODO: Move cleared objects into "processed" file - remove need for os
                segment_id = obj.get("segment_id")
                if segment_id > self.latest_segment_id:
                    for claim in obj.get("claims_found", []):
                        claims_found.append((claim, segment_id))
                    self.latest_segment_id = segment_id
        return claims_found

    def run(self):
        while True:

            if self.check_for_change():
                claims_found = self.process()
                
                if claims_found:
                    for claim, segment_id in claims_found:
                        print(claim, segment_id)
                        run_perplexity(claim, "./claim-analysis/automatic-citing/formatted.json")
                        # TODO: Error handling here if claims are not actually checked due to perplexity faults

            time.sleep(10) # TODO: Accurate time for updates, or alternate method needed

if __name__ == "__main__":
    processor = ExtractedProcessor(INPUT_FILE)
    processor.run()