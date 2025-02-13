import whisper
import subprocess
# from pydub import AudioSegment
import os
import queue
import time
import threading


class RecordingException(Exception):
    pass

class FileException(Exception):
    pass

class InvalidURL(Exception):
    pass


class AudioRecorder:

    def __init__(self, URL: str ="http://media-ice.musicradio.com/LBCUK", model_type: str = "base"):
        self.__URL = URL

        self.__to_transcribe = queue.Queue()

        # base < small < medium < large
        if model_type in ["base", "small", "medium", "large"]:
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



    def __check_URL(self) -> bool:

        print("Checking URL...")

        process = subprocess.run(
            ["ffmpeg", "-y", "-i", self.__URL, "-t", "1", "-f", "null", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            raise InvalidURL("The URL stream appears to be invalid.")
        


    def set_URL(self, URL: str):
        try:
            self.__check_URL(URL)
            self.__URL = URL
        
        except InvalidURL as e:
            print('No change has been applied:')
            print(str(e))
        
        

    def __record_audio(self, duration: int = 30, output_path: str = "./audio-files/temp.aac", overlap: int = 2):

        if duration <= 0:
            duration = 30

        print('Recording Audio...')


        subprocess.Popen(["ffmpeg", "-y", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5",
            "-i", self.__URL, "-t", str(duration), "-c:a", "aac", "-b:a", "128k", output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # waiting till recording has almost finished to start next one
        time.sleep(duration - overlap)



    def __AAC_to_WAV(self, AAC_path : str = "./audio-files/temp.aac", WAV_path : str = "./audio-files/temp.wav"):

        if os.path.exists(AAC_path):
            subprocess.run(["ffmpeg", "-y", "-i", AAC_path, "-ac", "1", "-ar", "16000", "-f", "wav", WAV_path],stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            raise FileException("No AAC file found, " + AAC_path)



    def __transcribe_audio(self, WAV_path : str = "./audio-files/temp.wav") -> str:

        if os.path.exists(WAV_path):
            print('Transcribing...')
            result = self.model.transcribe(WAV_path)
            return result["text"]
        else:
            raise FileException("No WAV file found, " + WAV_path)
    


    def __conti_record_audio(self, duration: int = 30, overlap: int = 2, starting_val: int = 0):
        num_file = starting_val

        while True:
            identifier = "audio" + str(num_file) 

            try:
                self.__record_audio(output_path=( "./audio-files/" + identifier + ".aac"), duration=duration, overlap=overlap)
                num_file += 1
                num_file %= 100
                self.__to_transcribe.put(identifier)

            except RecordingException as e:
                print("A recording has been skipped:\n" + str(e))




    def __conti_transcribe_audio(self, delete_audio: bool = True):

        while True:
            if not self.__to_transcribe.empty():
                name = self.__to_transcribe.get()

                try:
                    AAC_path = "./audio-files/" + name + ".aac"
                    WAV_path = "./audio-files/" + name + ".wav"

                    self.__AAC_to_WAV(AAC_path, WAV_path)

                    if os.path.exists(AAC_path):
                        os.remove(AAC_path)

                    transcript = self.__transcribe_audio(WAV_path)

                    with open("./transcript-files/" + name + "_transcript.txt", "w", encoding="utf-8") as f:
                        f.write(transcript)

                    print()
                    print(transcript)
                    print()

                    if delete_audio:
                        os.remove(WAV_path)
                
                except FileException as e:
                    print('Failed to transcribe a recording: \n' + str(e))
                


    def start(self, duration: int = 30, overlap: int = 2, delete_audio: bool = True, starting_value: int = 0):
            record_thread = threading.Thread(target=self.__conti_record_audio, args=(duration, overlap, starting_value))
            record_thread.daemon = True  
            record_thread.start()

            transcribe_thread = threading.Thread(target=self.__conti_transcribe_audio, args=(delete_audio,))
            transcribe_thread.daemon = True  
            transcribe_thread.start()


            while True:
                time.sleep(1)



audio = AudioRecorder()
audio.start(delete_audio=False, starting_value=16)





