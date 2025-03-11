import json
import whisper
import os

model = whisper.load_model("small")
WAV_path = ""
output_path_chunk = ""
output_path_whole = ""


if os.path.exists(WAV_path):
    transcript = model.transcribe(WAV_path, temperature=0.1)
        
        
    chunk_data = ({"id": id, "chunk": transcript})


    with open(output_path_chunk, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=4)


    with open(output_path_whole, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=4)