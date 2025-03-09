import logging
import json
import os
import time
from together import Together
key = os.getenv("TOGETHER_KEY")
together_client  = Together(api_key = key)


logging.basicConfig(
    filename="filtering.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def together_function(claim):
    system_message = """Is the following claim fact-checkable? Claims about the time, sentences from claims, etc. should be ignored. Respond with 1 for fact-checkable or 0 for not fact-checkable."""
    user_message = f"""Claim:{claim}"""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]    
    response = together_client.chat.completions.create(
        model= "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        max_tokens=1,
        temperature=0,
        top_p=1,
        top_k=1,
        repetition_penalty=0,
        stop=["<|eot_id|>"],
        stream=False
    )
    logging.info(f"Together API response for {claim}: {response}")
    return response.choices[0].message.content.strip() == "1"

def process_json_and_check_claims(json_file_path, output_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    filtered_data = []
    remaining_data = []  # Claims not processed in this cycle

    for entry in data:
        checkable = []
        for claim in entry["claims"]:
            if together_function(claim):
                checkable.append(claim)
            else:
                logging.info(f"Chunk number {entry.get('id')} - Claim '{claim}' was removed")
        if checkable:
            entry['claims'] = checkable
            filtered_data.append(entry)
        else:
            remaining_data.append(entry)
    
    with open(output_file_path, 'w') as f:
        json.dump(filtered_data, f, indent=4)
    
    with open(json_file_path, 'w') as f:
        json.dump(remaining_data, f, indent=4)

def monitor_extracted_claims(input_file, output_file, interval=10):
    last_modified = os.path.getmtime(input_file)
    print("Monitoring", input_file)
    while True:
        time.sleep(interval)
        current_modified = os.path.getmtime(input_file)
        if current_modified > last_modified:
            print("Change detected in", input_file)
            process_json_and_check_claims(input_file, output_file)
            last_modified = os.path.getmtime(input_file)

if __name__ == "__main__":
    extracted_claims_file = 'extracted_claims.json'
    filtered_claims_file = 'filtered_claims.json'
    monitor_extracted_claims(extracted_claims_file, filtered_claims_file)