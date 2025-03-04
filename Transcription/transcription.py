import whisper
import subprocess
import os
import queue
import time
import threading
import re
import json


class RecordingException(Exception):
    pass

class FileException(Exception):
    pass

class InvalidURL(Exception):
    pass



def remove_trailing_punc(transcript):
    i = 1
    while not transcript[-i].isalnum():
        i += 1

    if i == 1:
        final = transcript
    else:
        final = transcript[:-i + 1]
    if i > 1:
        removed = transcript[-i + 1:]
    else:
        removed = ""

    return final, removed



class TranscriptExporter:
    def __init__(self, delete_previous: bool = True, chunk_path: str = "transcript_chunks.json", whole_path: str = "transcript_whole.json"):
        self.__chunk_path = chunk_path
        self.__whole_path = whole_path

        if delete_previous:
            self.delete_records()


    def update_chunks(self, chunk: str):
        data = []
        
        if os.path.exists(self.__chunk_path):
            with open(self.__chunk_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        if len(data) > 0:
            id = data[-1]["id"] + 1
        else:
            id = 0

        data.append({"id": id, "chunk": chunk})


        with open(self.__chunk_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


    def update_whole_transcript(self, extra_transcript):
        data = ""
        
        if os.path.exists(self.__whole_path):
            with open(self.__whole_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        data += extra_transcript

        with open(self.__whole_path, "w", encoding="utf-8") as f:
            json.dump(data, f)


    def delete_records(self):
        if os.path.exists(self.__chunk_path):
            os.remove(self.__chunk_path)

        if os.path.exists(self.__whole_path):
            os.remove(self.__whole_path)



class TranscriptProcessor:
    
    def __init__(self):
        self.__raw_transcripts = []
        self.__final_transcripts = []
        self.__whole_transcript = ""
        self.__removed = ""
        self.__overlapping = []


    def new_transcript(self, transcript: str, overlap: int = 200):
        self.__raw_transcripts.append(transcript)

        if self.__final_transcripts:
            text2 = self.__merge_transcripts(transcript)
        else:
            text2 = transcript

        final, removed = remove_trailing_punc(text2)
        self.__removed = removed
        self.__final_transcripts.append(final)

        chunk = self.__whole_transcript[-overlap:] + final

        self.__whole_transcript += final

        self.__overlapping.append(chunk)

        return chunk, final


    def clean_text(self, text):
        return re.sub(r'[^\w\s]', '', text).lower()


    def __merge_transcripts(self, transcript):
        common_letters = self.__find_overlap(self.__final_transcripts[-1], transcript)

        if common_letters:
            transcript = self.__remove_overlap(transcript, common_letters)
        
        i = 0
        while i < len(transcript) and not transcript[i].isalpha():
            i += 1
        
        if i < len(transcript):
            if transcript[i].isupper():
                transcript = self.__removed + transcript

        return transcript


    def __find_overlap(self, text1, text2):

        clean0, clean1 = self.clean_text(text1).split(' '), self.clean_text(text2).split(' ')

        
        clean0 = [x for x in clean0 if x.strip()]
        clean1 = [x for x in clean1 if x.strip()]

        max_found = 0

        for i in range(1, min(20, min(len(clean0), len(clean1)))):
            matches = True
            for word_i in range(i):
                if clean0[len(clean0) - i + word_i] != clean1[word_i]:
                    matches = False
                    break

            if matches:
                max_found = i

        if max_found > 0:
            return "".join(clean1[:max_found])
        

    def __remove_overlap(self, transcript, letters):
        i = 0
        j = 0

        while i < len(transcript) and j < len(letters):
            if transcript[i].lower() == letters[j]:
                j += 1
            i += 1

        return transcript[i:]




class AudioTranscriber:

    def __init__(self, refiner, exporter, URL: str ="http://media-ice.musicradio.com/LBCUK", model_type: str = "base"):
        self.__URL = URL

        self.__refiner = refiner

        self.__exporter = exporter

        self.__to_transcribe = queue.Queue()

        self.__model_type = model_type

        # base < small < medium < large
        if model_type in ["base", "small", "medium", "large", "large-v2"]:
            self.model = whisper.load_model(model_type)

        else:
            print('Incorrect model type parameter, using the base type')
            self.model = whisper.load_model("base")

        try:
            self.__check_URL()


        except InvalidURL as e:
            print(str(e))
            print("Defaulting to http://media-ice.musicradio.com/LBCUK")
            self.__URL = "http://media-ice.musicradio.com/LBCUK"



    def __check_URL(self, URL = None) -> bool:

        if URL == None:
            URL = self.__URL

        print("Checking URL...")

        process = subprocess.run(["ffmpeg", "-y", "-i", URL, "-t", "1", "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:
            raise InvalidURL("The URL stream appears to be invalid.")
        


    def set_URL(self, URL: str):

        try:
            self.__check_URL(URL)
            self.__URL = URL
        
        except InvalidURL as e:
            print('No change has been applied:')
            print(str(e))
        
        

    def __record_audio_syncronous(self, output_path: str = "./audio-files/temp.aac", duration: int = 30, identifier: str = "temp.aac"):
        if duration <= 0:
            duration = 30


        subprocess.Popen(["ffmpeg", "-y", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5",
            "-i", self.__URL, "-t", str(duration), "-c:a", "aac", "-b:a", "128k", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        time.sleep(duration)
        self.__to_transcribe.put(identifier)



 
    def __transcribe_audio(self, WAV_path : str = "./audio-files/temp.wav", num: int = 0) -> str:

        if os.path.exists(WAV_path):

            if num > 0:
                with open("./transcript-files/audio" + str(num - 1) + "_transcript.txt", "r", encoding="utf-8") as f:
                            previous = " ".join(f.read().split()[-50:])

                previous, _ = remove_trailing_punc(previous)
     
                result = self.model.transcribe(WAV_path, temperature=0.1, initial_prompt=previous)

            else:
                result = self.model.transcribe(WAV_path, temperature=0.1)


 
            return result["text"]
        
        else:
            raise FileException("No WAV file found, " + WAV_path)
    



    def __AAC_to_WAV(self, AAC_path : str = "./audio-files/temp.aac", WAV_path : str = "./audio-files/temp.wav"):

        if os.path.exists(AAC_path):
            subprocess.run(["ffmpeg", "-y", "-i", AAC_path, "-ac", "1", "-ar", "16000", "-f", "wav", WAV_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            raise FileException("No AAC file found, " + AAC_path)




    def __conti_record_audio_overlap(self, duration: int = 45, overlap = 0.5, starting_val: int = 0):
        num_file = starting_val

        while True:

            try:
                identifier = "audio" + str(num_file) 
                thread0 = threading.Thread(target=self.__record_audio_syncronous, args=("./audio-files/" + identifier + ".aac", duration, identifier))
                thread0.start()
                num_file += 1
                num_file %= 100


            except RecordingException as e:
                print("A recording has been skipped:\n" + str(e))

            time.sleep(duration - overlap)



    def __conti_transcribe_audio(self, delete_audio: bool = True, transcript_overlap: int = 200):

        while True:
            if not self.__to_transcribe.empty():
                name = self.__to_transcribe.get()
                AAC_path = "./audio-files/" + name + ".aac"
                WAV_path = "./audio-files/" + name + ".wav"

                while not os.path.exists(AAC_path):
                    time.sleep(1)

                try:

                    self.__AAC_to_WAV(AAC_path, WAV_path)

                    if os.path.exists(AAC_path):
                        os.remove(AAC_path)

                    transcript = self.__transcribe_audio(WAV_path, int(name[-1]))

                    with open("./transcript-files/" + name + "_transcript.txt", "w", encoding="utf-8") as f:
                        f.write(transcript)
                    

                    chunk, extra_transcript = self.__refiner.new_transcript(transcript, transcript_overlap)

                    self.__exporter.update_chunks(chunk)
                    self.__exporter.update_whole_transcript(extra_transcript)

                    if delete_audio:
                        os.remove(WAV_path)
                
                except FileException as e:
                    print('Failed to transcribe a recording: \n' + str(e))
                



    def start(self, duration: int = 45, overlap = 0.5, delete_audio: bool = True, starting_value: int = 0, transcript_overlap: int = 200):
        record_thread = threading.Thread(target=self.__conti_record_audio_overlap, args=(duration, overlap, starting_value))
        record_thread.daemon = True  
        record_thread.start()


        transcribe_thread = threading.Thread(target=self.__conti_transcribe_audio, args=(delete_audio, transcript_overlap))
        transcribe_thread.daemon = True  
        transcribe_thread.start()


        while True:
            time.sleep(1)


exporter = TranscriptExporter()
refiner = TranscriptProcessor()

audio = AudioTranscriber(refiner=refiner, exporter=exporter, model_type="small")
audio.start(delete_audio=False, overlap=0.5, duration=45, transcript_overlap=200)


