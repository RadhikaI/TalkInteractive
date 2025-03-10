from typing import List, Dict, Tuple
from utils import *
import quote_support
import scorer

def score_claim(claim, evidence_pairs):
    print(f"CLAIM: {claim}")
    support_reliability_pairs = quote_support.generate_support_reliability_pairs(claim, evidence_pairs)
    print(support_reliability_pairs)
    score = scorer.score(support_reliability_pairs)
    print(score)
    return score

def score_from_first_query(query_json):
    claim = query_json.get("original_claim")
    # explanation = query_json.get("perplexity_response")
    evidence_pairs = query_json.get("citations")
    evidence_pairs = [{"source": x.get("url"), "evidence": x.get("evidence")} for x in evidence_pairs]
    return score_claim(claim, evidence_pairs)

def add_score_to_JSON(query_json):
    score = score_from_first_query(query_json)
    query_json["score"] = score
    return query_json

# claim = "Nigel Farage has stood for a re-election in the UK Parliament three times."
# evidence_pairs = [
#     {
#         "source": "https://en.wikipedia.org/wiki/Electoral_history_of_Nigel_Farage",
#         "evidence": "Farage has stood for election to the House of Commons eight times, in six general elections and two by-elections, losing in every attempt until 2024 in Clacton."
#     },
#     {
#         "source": "https://en.wikipedia.org/wiki/Nigel_Farage",
#         "evidence": "Farage was unsuccessful in his bid to become MP for South Thanet although he came second (beating Labour by over 4,000 votes), reduced the Conservative majority to less than 3,000, and gained over 32% of the vote."
#     },
#     {
#         "source": "https://www.britannica.com/biography/Nigel-Farage",
#         "evidence": "In 2024 Farage won a seat in the British Parliament, representing Clacton."
#     },
#     {
#         "source": "https://members.parliament.uk/member/5091/electionresult",
#         "evidence": "Nigel Farage is the Reform UK MP for Clacton, and has been an MP continually since 4 July 2024."
#     }
# ]

# score_claim(claim, evidence_pairs)

# import json

# with open("./claim-analysis/cited_claims.json", 'r') as file:
#     data = json.load(file)
# print(data)
# for x in data:
#     print(f"NEW CLAIM")
#     # score_from_first_query(x)
#     # json2 = add_score_to_JSON(x)
#     x = add_score_to_JSON(x)
#     # with open("scorer_output.json", 'w', encoding='utf-8') as f:
#     #     json.dump(json2, f, indent=4)
# with open("./claim-analysis/scorer_output.json", 'w', encoding='utf-8') as f:
#     json.dump(data, f, indent=4)

import json
import time
import os


# INPUT_FILE = "./claim-analysis/test2.json" 
# OUTPUT_FILE = "./claim-analysis/test3.json" 

INPUT_FILE = "./claim-analysis/cited_claims.json"
OUTPUT_FILE = "./claim-analysis/scorer_output.json"

class ScoreTagger:
    def __init__(self, input_file=INPUT_FILE, output_file=OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        
        self.latest_modified = os.path.getmtime(input_file)
        
        if not os.path.exists(self.output_file) or not is_JSON(self.output_file):
            with open(self.output_file, 'w') as f:
                json.dump([], f, indent=4)

    def check_for_change(self):

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

    def write_processed_segments(self, segments):
        with open(self.output_file, 'r') as f:
            processed_segments = json.load(f)
        for segment in segments:
            processed_segments.append(segment)
        with open(self.output_file, 'w') as f:
            json.dump(processed_segments, f, indent=4)

    # removes first k entries from the input file
    def remove_from_input_file(self, k):
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        data = data[k:] if len(data) > k else []
        with open(self.input_file, 'w') as f:
            json.dump(data, f, indent=4)

    def process(self):
        with open(self.input_file, 'r') as f:
            segment_data = json.load(f)
        
        tagged_data = []
        for obj in segment_data:
            tagged_data.append(add_score_to_JSON(obj))
        
        self.remove_from_input_file(len(tagged_data))

        return tagged_data
    
    
    def run(self):
        while True:
            if self.check_for_change():
                tagged_data = self.process()
                self.write_processed_segments(tagged_data)

            # print("SLEEPING")
            time.sleep(1)

if __name__ == "__main__":
    time.sleep(90) # Takes at least a minute till transcription starts
    print("Scorer running")
    processor = ScoreTagger()
    processor.run()