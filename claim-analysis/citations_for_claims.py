from sonar_response import run_perplexity
import json
import time
import os

INPUT_FILE = "./extracted_claims.json"
PROCESSED_FILE = "claim-analysis/automatic-citing/sample-processed.json"

class ExtractedProcessor:
    def __init__(self, input_file):
        """Initialise processor with tracking variables"""
        self.input_file = input_file
        self.processed_file = PROCESSED_FILE

        # File modification time used to detect changes
        # Watchdog, file handling libraries not used due to varied OS compatability
        self.latest_modified = os.path.getmtime(input_file)
        
        # No removal of segments
        self.last_processed_index = 0

        if not os.path.exists(self.processed_file):
            with open(self.processed_file, 'w') as f:
                json.dump([], f, indent=4)

    def write_processed_segment(self, segment):
        """Backs up processed segments"""
        with open(self.processed_file, 'r') as f:
            processed_segments = json.load(f)
        processed_segments.append(segment)
        with open(self.processed_file, 'w') as f:
            json.dump(processed_segments, f, indent=4)

    def check_for_change(self):
        """Detects if input file has been modified, i.e. new claims have been extracted."""
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

        if not data:
            return False

        current_modified = os.path.getmtime(self.input_file)
        diff = current_modified - self.latest_modified
        # print("LATEST:", self.latest_modified, "CURRENT:", current_modified, "DIFFERENCE:", diff)
        if diff > 0:
            self.latest_modified = current_modified
            return True
        return False


    def process(self):
        """Collects new segments based on their ID to be cited."""
        with open(self.input_file, 'r') as f:
            segment_data = json.load(f)
        total_segments = len(segment_data)
        
        new_segments = segment_data[self.last_processed_index:]
        print(f"Processing segments from index {self.last_processed_index} to {total_segments}")

        claims_by_segment = {}
        for _, obj in enumerate(new_segments):
            segment_id = obj.get("id")
            context = obj.get("chunk")
            if segment_id not in claims_by_segment:
                claims_by_segment[segment_id] = {"context": context, "claims": []}
            claims_by_segment[segment_id]["claims"].extend(obj.get("claims", []))
        
        self.last_processed_index = total_segments # Move pointer
        return claims_by_segment

    def run(self):
        while True:
            if self.check_for_change():
                print("New claims detected in extracted_claims.json")
                claims_by_segment = self.process()
                for segment_id, data in claims_by_segment.items():
                    context = data["context"]
                    claims = data["claims"]
                    for claim in claims:
                        run_perplexity(claim, "./claim-analysis/cited_claims.json")
                    self.write_processed_segment({
                        "id": segment_id,
                        "context": context,
                        "processed_claims": claims,
                    })
                    print(f"Processed claims: {claims}")
            time.sleep(5)  

if __name__ == "__main__":
    processor = ExtractedProcessor(INPUT_FILE)
    processor.run()