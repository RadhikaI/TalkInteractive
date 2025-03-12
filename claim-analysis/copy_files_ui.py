import shutil
import json
import time
import os
from threading import Thread

def copy_citations(source, dest, interval=10):
    """Copies finalised citation data (including scoring)"""
    while True:
        shutil.copy2(source, dest)
        time.sleep(interval)

def copy_transcript_txt(source, dest, interval=5):
    """Transforms whole transcript JSON into text file to be displayed."""
    while True:
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            with open(source, 'r', encoding='utf-8') as json_file:
                try:
                    # Try parsing as JSON
                    content = json.load(json_file)
                except json.JSONDecodeError:
                    json_file.seek(0)
                    content = json_file.read() # Read as plain text instead
                
                with open(dest, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(content)
                    
        except Exception as e:
            print(f"Error copying JSON content: {e}")
        time.sleep(interval)

def start_claims_thread(source, dest, interval=20):
    copy_thread = Thread(
        target=copy_citations,
        args=(source, dest, interval),
        daemon=True
    )
    copy_thread.start()
    return copy_thread

def start_transcript_thread(source, dest, interval=5):
    copy_thread = Thread(
        target=copy_transcript_txt,
        args=(source, dest, interval),
        daemon=True
    )
    copy_thread.start()
    return copy_thread

if __name__ == "__main__":
    CLAIM_INPUT_FILE = "claim-analysis/scorer_output.json"
    CLAIM_OUTPUT_FILE = "front-end/src/data"
    
    TRANSCRIPT_INPUT_FILE = "transcript_whole.json"
    TRANSCRIPT_OUTPUT_FILE = "front-end/src/data/transcript_whole.txt"
    
    start_claims_thread(CLAIM_INPUT_FILE, CLAIM_OUTPUT_FILE)
    start_transcript_thread(TRANSCRIPT_INPUT_FILE, TRANSCRIPT_OUTPUT_FILE)
    
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("File copying stopped") # Threads will automatically stop when main thread exits.