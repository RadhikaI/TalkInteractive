from typing import List, Dict, Tuple
from utils import *
import quote_support
import scorer
import json
import time
import os

INPUT_FILE = "./claim-analysis/cited_claims.json"
OUTPUT_FILE = "./claim-analysis/scorer_output.json"

logging.basicConfig(
    filename="./claim-analysis/sonar_check.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def score_claim(claim: str, evidence_pairs: List[Dict[str, str]]) -> int:
    print(f"CLAIM: {claim}")
    support_reliability_pairs = quote_support.generate_support_reliability_pairs(claim, evidence_pairs)
    print(support_reliability_pairs)
    score = scorer.score(support_reliability_pairs)
    print(score)
    return score

def score_from_first_query(query_json: json) -> int:
    claim = query_json.get("original_claim")
    # explanation = query_json.get("perplexity_response")
    evidence_pairs = query_json.get("citations")
    evidence_pairs = [{"source": x.get("url"), "evidence": x.get("evidence")} for x in evidence_pairs]
    return score_claim(claim, evidence_pairs)

def add_score_to_JSON(query_json: json) -> json:
    score = score_from_first_query(query_json)
    query_json["score"] = score
    return query_json



class ScoreTagger:
    def __init__(self, input_file: str = INPUT_FILE, output_file: str = OUTPUT_FILE) -> None:
        self.input_file = input_file
        self.output_file = output_file
        
        self.latest_modified = os.path.getmtime(input_file)
        
        if not os.path.exists(self.output_file) or not is_JSON(self.output_file):
            with open(self.output_file, 'w') as f:
                json.dump([], f, indent=4)

    def check_for_change(self) -> bool:

        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
        if not data:
            return False 

        current_modified = os.path.getmtime(self.input_file)
        print("LATEST", self.latest_modified, "CURRENT", current_modified)
        if self.latest_modified < current_modified:
            self.latest_modified = current_modified
            return True
        return False

    # takes a list of JSONs
    def write_processed_segments(self, segments: List) -> None:
        try:
            with open(self.output_file, 'r') as f:
                processed_segments = json.load(f)
        except (FileNotFoundError):
            logging.error(f"Error: Output file {self.output_file} does not exist")
            raise
        except (json.decoder.JSONDecodeError):
            logging.error(f"Error: Output file {self.output_file} is not formatted as a JSON")
            raise
        for segment in segments:
            processed_segments.append(segment)
        with open(self.output_file, 'w') as f:
            json.dump(processed_segments, f, indent=4)

    # removes first k entries from the input file
    def remove_from_input_file(self, k: int) -> None:
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        data = data[k:] if len(data) > k else []
        with open(self.input_file, 'w') as f:
            json.dump(data, f, indent=4)

    # returns list of JSONs
    def process(self) -> List:
        with open(self.input_file, 'r') as f:
            segment_data = json.load(f)
        
        tagged_data = []
        for obj in segment_data:
            tagged_data.append(add_score_to_JSON(obj))
        
        self.remove_from_input_file(len(tagged_data))

        return tagged_data
    
    
    def run(self) -> None:
        while True:
            if self.check_for_change():
                tagged_data = self.process()
                self.write_processed_segments(tagged_data)

            # print("SLEEPING")
            time.sleep(1)

if __name__ == "__main__":
    # time.sleep(90) # If needed
    print("Scorer running")
    tagger = ScoreTagger()
    tagger.run()