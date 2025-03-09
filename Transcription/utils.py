import whisper
import subprocess
import os
import queue
import time
import threading
import re
import json
import logging

logging.basicConfig(
    filename="transcription.log", 
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("transcription.py started.")


os.makedirs("./audio-files", exist_ok=True)
os.makedirs("./transcript-files", exist_ok=True)
os.makedirs("./saved-files", exist_ok=True)


def remove_trailing_punc(transcript: str):
    """Function to remove punctuation at the end of a string, and returns result and string removed."""
    i = 1

    while i < len(transcript) and (not transcript[-i].isalnum()):
        i += 1

    if i == 1:
        final = transcript
        removed = ""
    else:
        final = transcript[:-i + 1]
        removed = transcript[-i + 1:]

    return final, removed
