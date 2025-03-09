from utils import *


class TranscriptExporter:
    """Handles exporting transcripts to JSON files"""

    def __init__(self, delete_previous: bool = True, chunk_path: str = "transcript_chunks.json", whole_path: str = "transcript_whole.json"):

        logging.info(f"TranscriptExporter initialized with delete_previous={delete_previous}.")

        self.__chunk_path = chunk_path
        self.__whole_path = whole_path

        # should the new transcript be added to fresh files (previous saved).
        if delete_previous:
            self.delete_and_save_records()


    def update_chunks(self, chunk: str):
        """ Update the file containing chunks"""
        logging.info(f"update_chunks called with chunk={chunk}.")

        data = []
        
        if os.path.exists(self.__chunk_path):
            with open(self.__chunk_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        else:
            logging.error(f"{self.__chunk_path} is not found, creating file.")

        # ensure the next id is one more than previous
        if len(data) > 0:

            if data and isinstance(data[-1], dict) and "id" in data[-1] and isinstance(data[-1]["id"], int):
                id = data[-1]["id"] + 1

            else:
                logging.error(f"{self.__chunk_path} in unexpected format, clearing and saving records.")
                self.delete_and_save_records()

        else:
            id = 0


        data.append({"id": id, "chunk": chunk})


        with open(self.__chunk_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


    def update_whole_transcript(self, extra_transcript):
        """Update the file containing whole transcript"""

        logging.info(f"update_whole_transcript called with extra_transcript={extra_transcript}.")


        data = ""

        if os.path.exists(self.__whole_path):
            with open(self.__whole_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        else:
            logging.error(f"{self.__whole_path} not found, creating file.")

        if isinstance(data, str):
            data += extra_transcript

        else:
            logging.error(f"{self.__whole_path} in unexpected format, clearing and saving records.")
            self.delete_and_save_records()


        with open(self.__whole_path, "w", encoding="utf-8") as f:
            json.dump(data, f)



    def delete_and_save_records(self):
        """To save previous record, and clear working files"""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        logging.info(f"Clearing and saving records with timestamp {timestamp}.")

        if os.path.exists(self.__chunk_path):
            try:
                with open(self.__chunk_path, "r") as f:
                    content = json.load(f)
                    
                if content:
                    backup_path = "./saved-files/chunks_" + timestamp + ".json"
                    with open(backup_path, "w") as f:
                        json.dump(content, f)

            except (json.JSONDecodeError, FileNotFoundError):
                content = []
                
            with open(self.__chunk_path, "w") as f:
                json.dump([], f, indent=4)

        else:
            logging.error(f"No file found under {self.__chunk_path}, creating new file.")

            with open(self.__chunk_path, "w") as f:
                json.dump([], f, indent=4)
        

        if os.path.exists(self.__whole_path):
            try:
                with open(self.__whole_path, "r") as f:
                    content = json.load(f)
                    
                if content:
                    backup_path = "./saved-files/whole_" + timestamp + ".json"
                    with open(backup_path, "w") as f:
                        json.dump(content, f)

            except (json.JSONDecodeError, FileNotFoundError):
                content = ""
                
            with open(self.__whole_path, "w") as f:
                json.dump("", f, indent=4)

        else:
            with open(self.__whole_path, "w") as f:
                json.dump("", f, indent=4)

            logging.error(f"No file found under {self.__whole_path}, creating new file.")




class TranscriptProcessor:
    """Processes raw transcript files"""
    
    def __init__(self):
        self.__raw_transcripts = []
        self.__final_transcripts = []
        self.__whole_transcript = ""
        self.__removed = ""
        self.__overlapping = []

        logging.info("TranscriptProcessor file instanciated.")



    def new_transcript(self, transcript: str, overlap: int = 200):
        """Called when a new transcript is produced, and returns the chunk and no overlapping section (to be added to whole)."""
        
        logging.info(f"new_transcript called with transcript={transcript}, overlap={overlap}.")


        self.__raw_transcripts.append(transcript)

        if self.__final_transcripts:
            text2 = self.__merge_transcripts(transcript)

        else:
            text2 = transcript


        non_overlapping, removed = remove_trailing_punc(text2)
        self.__removed = removed
        self.__final_transcripts.append(non_overlapping)

        chunk = self.__whole_transcript[-overlap:] + non_overlapping

        self.__whole_transcript += non_overlapping

        self.__overlapping.append(chunk)

        return chunk, non_overlapping



    def __clean_text(self, text: str) -> str:
        """Clean punctuation, whitespace etc, for word matching at the join (returns result)."""

        return re.sub(r'[^\w\s]', '', text).lower()



    def __merge_transcripts(self, transcript: str) -> str:
        """Remove duplicates from the end of the last transcript (returns result)."""

        common_letters = self.__find_overlap(self.__final_transcripts[-1], transcript)

        if common_letters:
            transcript = self.__remove_overlap(transcript, common_letters)
        
        i = 0
        while i < len(transcript) and transcript[i].isspace():
            i += 1

        if i >= len(transcript):
            return transcript

        if transcript[i].isalnum() and transcript[i].isupper():
            print('hellooo')
            transcript = self.__removed + transcript


        return transcript



    # TODO: make more readable and check
    def __find_overlap(self, text1: str, text2: str) -> str:
        """Find the overlap between two cleaned transcripts, and return alphanumeric letters to be removed."""

        clean0, clean1 = self.__clean_text(text1).split(' '), self.__clean_text(text2).split(' ')

        
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
        



    def __remove_overlap(self, transcript: str, letters: str) -> str:
        """Given alphanumeric characters in overlap, remove and return result."""

        i = 0
        j = 0

        consistent = True

        while i < len(transcript) and j < len(letters):
            if transcript[i].lower() == letters[j]:
                j += 1

            elif transcript.isalnum():
                consistent = False
                break

            i += 1

        if consistent:
            return transcript[i:]
        
        return transcript



class AudioTranscriber:
    """Manages audio recording and transcription."""

    def __init__(self, refiner, exporter, URL: str ="http://media-ice.musicradio.com/LBCUK", model_type: str = "base"):

        logging.info(f"AudioTranscriber object initalised with URL={URL}, model_type={model_type}.")

        self.__URL = URL

        self.__refiner = refiner

        self.__exporter = exporter

        self.__to_transcribe = queue.Queue()

        self.__model_type = model_type

        # base < small < medium < large
        if model_type in ["base", "small", "medium", "large", "large-v2"]:
            self.model = whisper.load_model(model_type)

        else:
            logging.error(f"Model type not reconised, defaulting to small.")
            self.model = whisper.load_model("small")

        self.__check_URL()


    def check_speed(self):
        """Check size of queue, and downgrades if transcription thread is not keeping up."""

        if self.__to_transcribe.qsize() > 3:
            possible_types = ["base", "small", "medium", "large", "large-v2"]
            position = possible_types.find(self.__model_type)
            
            if position > 0:
                logging.info(f"Transcribe queue has length {self.__to_transcribe.qsize()}, downgrading model from {self.__model_type} to {possible_types[position]}.")

                self.__model_type = possible_types[position]
                self.model = whisper.load_model(self.__model_type)
            


    def __check_URL(self, URL = None) -> bool:
        """Ensure the URL is valid (returns boolean)."""
        if URL == None:
            URL = self.__URL
            # logging.info(f"check_URL called with the object's URL={self.__URL}.")


        process = subprocess.run(["ffmpeg", "-y", "-i", URL, "-t", "1", "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:

            # check if known stream works
            test_process = subprocess.run(["ffmpeg", "-y", "-i", "http://media-ice.musicradio.com/LBCUK", "-t", "1", "-f", "null", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if test_process.returncode != 0:
                logging.error("Can't reach the audio streams, check internet.")

            else:
                logging.error("The URL stream appears to be invalid, defaulting to http://media-ice.musicradio.com/LBCUK")
                self.__URL = "http://media-ice.musicradio.com/LBCUK"
        
        
        

    def __record_audio_syncronous(self, output_path: str = "./audio-files/temp.aac", duration: int = 45, identifier: str = "temp.aac"):
        """Record the audio (blockign)."""

        if duration <= 0:
            logging.error(f"duration={duration}, defaulting to 45.")
            duration = 45

        logging.info(f"Recording to {output_path} starting...")

        subprocess.Popen(["ffmpeg", "-y", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5",
            "-i", self.__URL, "-t", str(duration), "-c:a", "aac", "-b:a", "128k", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(duration)
        logging.info(f"Recording to {output_path} finished.")

        self.__to_transcribe.put(identifier)



    def __transcribe_audio(self, WAV_path : str = "./audio-files/temp.wav", num: int = 0) -> str:
        """ Transcribe audio from WAV file, and text file of previous."""

        logging.info(f"transcribe_audio called with WAV_path={WAV_path}, num={num}")

        if os.path.exists(WAV_path):

            if num > 0:
                try:
                    with open("./transcript-files/audio" + str(num - 1) + "_transcript.txt", "r", encoding="utf-8") as f:
                        previous = " ".join(f.read().split()[-50:])
                        previous, _ = remove_trailing_punc(previous)

                except:
                    logging.error(f"Error in opening previous transcription, transcribing without.")
                    previous = ""

     
                result = self.model.transcribe(WAV_path, temperature=0.1, initial_prompt=previous)

            else:
                result = self.model.transcribe(WAV_path, temperature=0.1)


            return result["text"]
        
        else:
            logging.error(f"No WAV file found called {WAV_path} found to transcribe.")
    



    def __AAC_to_WAV(self, AAC_path : str = "./audio-files/temp.aac", WAV_path : str = "./audio-files/temp.wav"):

        logging.info(f"Converting AAC file {AAC_path} to WAV.")

        if os.path.exists(AAC_path):
            subprocess.run(["ffmpeg", "-y", "-i", AAC_path, "-ac", "1", "-ar", "16000", "-f", "wav", WAV_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            logging.error(f"No AAC file {AAC_path} found")




    def __conti_record_audio_overlap(self, duration: int = 45, overlap = 0.5, starting_val: int = 0):
        """Continously record overlapping audio clips."""

        logging.info(f"conti_record_audio_overlap called with duration={duration}, overlap={overlap}, starting_val={starting_val}.")

        num_file = starting_val

        while True:
            identifier = "audio" + str(num_file) 

            thread0 = threading.Thread(target=self.__record_audio_syncronous, args=("./audio-files/" + identifier + ".aac", duration, identifier))
            thread0.start()

            num_file += 1
            num_file %= 100

            time.sleep(duration - overlap)



    def __conti_transcribe_audio(self, delete_audio: bool = True, transcript_overlap: int = 200):
        """COntinously checks queue for audio clips, then transcribes, writes to txt, refines, and exports."""

        logging.info(f"conti_transcribe_audio called with delete_audio={delete_audio}, transcript_overlap={transcript_overlap}.")

        while True:
            self.check_speed()

            if not self.__to_transcribe.empty():
                name = self.__to_transcribe.get()
                AAC_path = "./audio-files/" + name + ".aac"
                WAV_path = "./audio-files/" + name + ".wav"

                self.__AAC_to_WAV(AAC_path, WAV_path)

                if os.path.exists(AAC_path):
                    os.remove(AAC_path)
                    logging.info(f"AAC file {WAV_path} removed.")

                transcript = self.__transcribe_audio(WAV_path, int(name[-1]))

                with open("./transcript-files/" + name + "_transcript.txt", "w", encoding="utf-8") as f:
                    f.write(transcript)
                    

                chunk, extra_transcript = self.__refiner.new_transcript(transcript, transcript_overlap)

                self.__exporter.update_chunks(chunk)
                self.__exporter.update_whole_transcript(extra_transcript)

                if delete_audio:
                    logging.info(f"WAV file {WAV_path} removed.")
                    os.remove(WAV_path)
                
                

    def start(self, duration: int = 45, overlap = 0.5, delete_audio: bool = True, starting_value: int = 0, transcript_overlap: int = 200):
        """Starts both the recording and transcribing threads."""

        logging.info(f"start called with duration={duration}, overlap={overlap}, delete_audio={delete_audio}, starting_value={starting_value}, transcript_overlap={transcript_overlap}.")

        record_thread = threading.Thread(target=self.__conti_record_audio_overlap, args=(duration, overlap, starting_value))
        record_thread.daemon = True  
        record_thread.start()


        transcribe_thread = threading.Thread(target=self.__conti_transcribe_audio, args=(delete_audio, transcript_overlap))
        transcribe_thread.daemon = True  
        transcribe_thread.start()


        while True:
            time.sleep(1)


    def from_wav_test(self, WAV_path: str, output_path_chunk: str, output_path_whole: str):

        if os.path.exists(WAV_path):
                transcript = self.model.transcribe(WAV_path, temperature=0.1)
        
        
        chunk_data = ({"id": id, "chunk": transcript})


        with open(output_path_chunk, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=4)


        with open(output_path_whole, "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=4)




        
