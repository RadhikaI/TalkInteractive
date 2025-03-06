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
    explanation = query_json.get("perplexity_response")
    evidence_pairs = query_json.get("citations")
    evidence_pairs = [{"source": x.get("url"), "evidence": x.get("evidence")} for x in evidence_pairs]
    return score_claim(claim, evidence_pairs)

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

import json

with open('./claim-analysis/automatic-citing/move-formatted.json', 'r') as file:
    data = json.load(file)
print(data)
for x in data:
    print(f"NEW CLAIM")
    score_from_first_query(x)
