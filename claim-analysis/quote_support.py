from utils import *

trusted_sources: Optional[Dict[str, int]] = None
SOURCE_TRUST_FILE = "./claim-analysis/source_trust.json"

def get_trusted_sources(filename: str = SOURCE_TRUST_FILE) -> None:
    global trusted_sources
    if trusted_sources is None:
        try:
            with open(filename, 'r') as f:
                trusted_sources = json.load(f)
        except (FileNotFoundError):
            logging.error(f"Error: Output file {filename} does not exist")
            raise
        except (json.decoder.JSONDecodeError):
            logging.error(f"Error: Output file {filename} is not formatted as a JSON")
            raise


def perplexity_prompt_printer(instruction_message: str, content_message: str) -> None:
    print(f"{instruction_message}\n{content_message}\n")

def query_support(claim: str, evidence: str) -> json:
    if claim is None or evidence is None:
        return None
    return perplexity_prompt(
        instruction_message = "You are provided with a claim followed by an evidence statement that may agree with or disagree with the claim, or it may be completely unrelated. Ignoring all other possible evidence for the claim, provide a 'support score' in the range [-1, +1] denoting the degree of support for the claim of the statement. -1 stands for complete disagreement, 0 for neutral, and +1 for complete agreement. You can provide any value in between. Be concise: simply provide the single number. If the evidence statement has nothing to do with the claim, say 'Irrelevant' instead.",
        content_message = "Claim: '" + claim + "', Evidence: '" + evidence + "'"
    )

def query_reliability(source: str) -> json:
    if source is None:
        return None
    return perplexity_prompt(
        instruction_message = "You are provided with the url of an online source from which information has been taken. Provide a 'reliability score' in the range [0, 1] denoting the reliability of the source. 0 stands for completely unknown and unreliable, 1 stands for completely reliable. You can provide any value in between. Be concise: simply provide the single number.",
        content_message = source
    )

# look up reliability in database of trust values for sources
def lookup_source_reliability(source: str) -> Optional[float]:
    s = normalize_url(source)
    get_trusted_sources()
    return trusted_sources.get(s, None)

def generate_support_reliability_pairs(claim: str, evidence_pairs: List[Dict[str, str]]) -> List[Dict[str, int]]:
    # Support scores
    support_scores = []
    for evidence_pair in evidence_pairs:
        response_json = query_support(claim, evidence_pair["evidence"])
        # print(f" for {claim} and {evidence_pair["evidence"]}")
        # print(response_json)
        # print()

        if isinstance(response_json, dict):
            support_scores.append(list_get(response_json.get("choices"), 0).get("message").get("content"))
        else:
            support_scores.append(None)

    # Reliability scores
    reliability_scores = []
    for evidence_pair in evidence_pairs:
        # look up in database first - if found, this overwrites the generated reliability
        r = lookup_source_reliability(evidence_pair["source"])
        if r is not None:
            # print(f" for {evidence_pair["source"]}")
            # print(f"Source found in database: {r}")
            # print()
            reliability_scores.append(r)
            continue

        response_json = query_reliability(evidence_pair["source"])
        # print(f" for {evidence_pair["source"]}")
        # print(response_json)
        # print()
        
        if isinstance(response_json, dict):
            reliability_scores.append(list_get(response_json.get("choices"), 0).get("message").get("content"))
        else:
            reliability_scores.append(None)
    
    return [{
        "support": validate_support(float_prefix(s)),
        "reliability": validate_reliability(float_prefix(r))
    } for s, r in zip(support_scores, reliability_scores)]




# Testing:
# Prompt to generate source-evidence pairs: "Nigel Farage has stood for a re-election in the UK Parliament three times." Provide evidence for and/or against. For each piece of evidence, provide both the url and the quote that supports or refutes the claim.
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
# print(generate_support_reliability_pairs(claim, evidence_pairs))


