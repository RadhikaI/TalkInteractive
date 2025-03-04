from sonar_response import run_perplexity
import json
import time
import os

# INPUT_FILE = "./claim-analysis/automatic-citing/sample.json"
# PROCESSED_FILE = "./claim-analysis/automatic-citing/sample-processed.json"

INPUT_FILE = "./claim-analysis/extracted_claims.json"
PROCESSED_FILE = "claim-analysis/automatic-citing/sample-processed.json"



class ExtractedProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.processed_file = PROCESSED_FILE
        
        self.latest_modified = os.path.getmtime(input_file)
        self.latest_segment_id = 0
        
        if not os.path.exists(self.processed_file):
            with open(self.processed_file, 'w') as f:
                json.dump([], f)

    def check_for_change(self):
        current_modified = os.path.getmtime(self.input_file)
        print("LATEST", self.latest_modified, "CURRENT", current_modified)

        if self.latest_modified < current_modified:
            self.latest_modified = current_modified
            return True
        return False

    def write_processed_segment(self, segment):
        with open(self.processed_file, 'r') as f:
            processed_segments = json.load(f)
        processed_segments.append(segment)
        with open(self.processed_file, 'w') as f:
            json.dump(processed_segments, f)

    def process(self):
        with open(self.input_file, 'r') as f:
            segment_data = json.load(f)
        
        claims_found = []
        objects_to_keep = []
        
        for obj in segment_data:
            segment_id = obj.get("id")
            context = obj.get("chunk")
            if segment_id > self.latest_segment_id:
                for claim in obj.get("claims", []):
                    claims_found.append((context, claim, segment_id))
            else:
                objects_to_keep.append(obj)
        
        with open(self.input_file, 'w') as f:
            json.dump(objects_to_keep, f)
        
        return claims_found

    def run(self):
        while True:
            if self.check_for_change():
                claims_found = self.process()
                
                for context, claim, segment_id in claims_found:
                    run_perplexity(claim, "./claim-analysis/automatic-citing/move-formatted.json")
                    
                    self.write_processed_segment({
                        "id": segment_id,
                        "context": context,
                        "processed_claim": [claim],
                    })
                    
                    if segment_id > self.latest_segment_id:
                        self.latest_segment_id = segment_id

                    # TODO : Add failures to different file to be reprocessed. 

            time.sleep(10)

if __name__ == "__main__":
    processor = ExtractedProcessor(INPUT_FILE)
    processor.run()