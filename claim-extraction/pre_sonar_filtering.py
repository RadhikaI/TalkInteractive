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

ERROR_FILE = "./claim-analysis/together_request_failures.json"

def save_claim(claim, context, response, file_path):
    entry = {"claim": claim, "context": context, "response": response}
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(entry)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def together_function(claim, context, max_retries=3, delay=2, additional_filtering=False):
    system_message = (
        """Return 1 if the following has a phrase that makes up an entire claim, i.e. something said that can be checked within the string claim. You should return 0 otherwise. Return 0 if these claims are also irrelevant to a fact checker, for example, claims from advertisements, about the current time or weather. """
    )

    if additional_filtering:
        system_message += " Return 2 if you believe the claim can be split up, and there is further claim extraction to be done."
    
    user_message = f"Claim:{claim}. Context:{context}"
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    attempt = 1
    while attempt <= max_retries:
        try:            
            response = together_client.chat.completions.create(
                model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                messages=messages,
                max_tokens=1,
                temperature=0,
                top_p=1,
                top_k=1,
                repetition_penalty=0,
                stop=["<|eot_id|>"],
                stream=False
            )
            
            specific_response = response.choices[0].message.content.strip()
            logging.info(f"Together API response for {claim}: {response}")

            return int(specific_response)

        except Exception as e:
            error_message = f"Error during API call (attempt {attempt}/{max_retries}): {str(e)}"
            logging.error(error_message)
            save_claim(claim, context, error_message, ERROR_FILE)
            
            if "Invalid API key" in str(e) or "AuthenticationError" in str(type(e)):
                logging.error(f"Authentication error detected. No retries made.")
                break
                
            attempt += 1
            time.sleep(delay)

    logging.warning(f"Could not test claim: '{claim}'. No filter checks were performed.")
    return -1 

def run_filtering(INPUT_FILE, OUTPUT_FILE):
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    filtered_data = []
    remaining_data = [] 
    for entry in data:
        checkable = []
        for claim in entry["claims"]:
            result = together_function(claim, entry["chunk"])
            if result == 1 or result == -1:  
                checkable.append(claim)
            else:
                logging.info(f"Chunk number {entry.get('id')} - Claim '{claim}' was removed")
        if checkable:
            entry['claims'] = checkable
            filtered_data.append(entry)
        else:
            remaining_data.append(entry)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(filtered_data, f, indent=4)
    
    with open(INPUT_FILE, 'w') as f:
        json.dump(remaining_data, f, indent=4)

def monitor_extracted_claims(INPUT_FILE, OUTPUT_FILE, interval=10):
    last_modified = os.path.getmtime(INPUT_FILE)
    print("Monitoring", INPUT_FILE)
    while True:
        time.sleep(interval)
        current_modified = os.path.getmtime(INPUT_FILE)
        if current_modified > last_modified:
            print("Change detected in", INPUT_FILE)
            run_filtering(INPUT_FILE, OUTPUT_FILE)
            last_modified = os.path.getmtime(INPUT_FILE)

if __name__ == "__main__":
    extracted_claims_file = 'extracted_claims.json'
    filtered_claims_file = 'filtered_claims.json'
    monitor_extracted_claims(extracted_claims_file, filtered_claims_file)