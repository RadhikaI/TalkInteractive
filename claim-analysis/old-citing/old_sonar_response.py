import requests
import logging
import os
import json
import re
import time

logging.basicConfig(
    filename="./claim-analysis/automatic-citing/auto_mover_sonar_response.log", 
    # filename = "./test-transcripts/testC.log",
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def perplexity_prompt(claim):
    url = "https://api.perplexity.ai/chat/completions"
    key = os.getenv("PERPLEXITY_KEY")

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": """You are provided with a claim. What evidence is there for or against this claim? 
            Be precise and concise: first state if it is supported, not supported, or partially supported/incorrect. There is no need to repeat what the claim is in your opening sentence; when considering the claim, focus on semantic accuracy, and in your output, focus on the evidence. 
            The structure of your output should start with a statement on if the claim is supported or not, and reasoning for this decision (citing sources). 
            Once you have written this paragraph, then the final section ("Evidence Mapping") of your output should be a mapping of the source URL to the EXACT sentence that is used FROM THE SOURCE as evidence. This must be done for all forms of media cited, including video sources. If there is no evidence, do not provide any citations."""},
            {"role": "user", "content": claim}
        ],
        "max_tokens": 300, 
        "temperature": 0.1,
        "top_p": 0.9,
        "search_domain_filter": None,
        "return_images": False,
        "return_related_questions": False,
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 
        logging.info(f"Perplexity API response: {response.status_code} - {response.text}")  
        return response.json() 
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred: {str(e)}")
        return "Error"
