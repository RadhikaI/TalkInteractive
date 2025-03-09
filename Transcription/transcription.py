from utils import *
from transcription_classes import *

if __name__ == "__main__":
    logging.info("transcription.py started.")
    
    os.makedirs("./audio-files", exist_ok=True)
    os.makedirs("./transcript-files", exist_ok=True)
    os.makedirs("./saved-files", exist_ok=True)

    exporter = TranscriptExporter()
    refiner = TranscriptProcessor()

    audio = AudioTranscriber(refiner=refiner, exporter=exporter, model_type="small")
    audio.start(delete_audio=False, overlap=0.5, duration=45, transcript_overlap=200)


