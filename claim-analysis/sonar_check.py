from typing import List, Dict, Tuple
from utils import *
import quote_support
import scorer

claim = "Nigel Farage has stood for a re-election in the UK Parliament three times."
evidence_pairs = [
    {
        "source": "https://en.wikipedia.org/wiki/Electoral_history_of_Nigel_Farage",
        "evidence": "Farage has stood for election to the House of Commons eight times, in six general elections and two by-elections, losing in every attempt until 2024 in Clacton."
    },
    {
        "source": "https://en.wikipedia.org/wiki/Nigel_Farage",
        "evidence": "Farage was unsuccessful in his bid to become MP for South Thanet although he came second (beating Labour by over 4,000 votes), reduced the Conservative majority to less than 3,000, and gained over 32% of the vote."
    },
    {
        "source": "https://www.britannica.com/biography/Nigel-Farage",
        "evidence": "In 2024 Farage won a seat in the British Parliament, representing Clacton."
    },
    {
        "source": "https://members.parliament.uk/member/5091/electionresult",
        "evidence": "Nigel Farage is the Reform UK MP for Clacton, and has been an MP continually since 4 July 2024."
    }
]

support_reliability_pairs = quote_support.generate_support_reliability_pairs(claim, evidence_pairs)
print(support_reliability_pairs)
score = scorer.score(support_reliability_pairs)
print(score)
