import whisper
import subprocess
# from pydub import AudioSegment
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




class TranscriptionRefiner:


    def __init__(self, transcription_overlap: int = 15):
        self.__raw_transcripts = []
        self.__final_transcripts = []
        self.__whole_transcript = ""
        self.__removed = ""
        self.__overlap = transcription_overlap
        self.__overlapping = []
        self.__id = 0


    def new_transcript(self, transcript):
        self.__raw_transcripts.append(transcript)
        if self.__final_transcripts:
            text2 = self.__merge_transcripts(transcript)
        else:
            text2 = transcript

        final, removed = remove_trailing_punc(text2)

        self.__final_transcripts.append(final)

        #TODO: add overlap of self.__overlap many words from the end of self.__whole_transcript, then export to JSON file (update singular JSON each time with new record for each transcript chunk), also update an whole transcript in a JSON or part of teh same

        overlapping = self.__whole_transcript[-150:] + final
        self.__overlapping.append(overlapping)
        self.__whole_transcript += final
        self.__removed = removed

        self.update_json(overlapping)


        print(self.__overlapping)
    

    def update_json(self, new_chunk, json_file: str = "transcript_chunks.json"):
        pass

        


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
                self.__whole_transcript += self.__removed


        return transcript


    # def __merge(self, text1, text2):
    #     common_letters = self.__find_overlap(text1, text2)
    #     if common_letters:
    #         return self.__remove_overlap(text2, common_letters)

    #     return text2

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

 
    def testing(self):
        



        # Example transcriptions
        transcriptions = [
            "who lost three of her limbs, and then there was that little girl, Hind Rajab, a five-year-old Palestinian girl in the Gaza Strip, in a car that had been hit by Israeli missiles as part of this war. All of her relatives in that car were dead. She made a call to an ambulance crew to try and get help. She was in there for days trying to get help and they couldn't get to her, and she died in that situation. Five years of age. Appalling. And as the last, like I said, as the last breath left her body, she experienced that the same way any child who's losing the last breath from their body would experience it. You're not Palestinian or Israeli or Jewish or Muslim.",
            "Jewish or Muslim in those situations. You're a beautiful child taking your last breath. And can we can we try and get to a point where that is where we stand when we talk about this rather than. Yeah, but Israel, yeah, but Palestine, yeah, but Hamas, yeah, but this, yeah, but that. We can have discussions about how we view the actions of Hamas and the Israeli government. I've had many. I'm having one today with you. I think Hamas are unspeakable. I think the Israeli this Israeli government current Israeli government has made dreadful mistakes in the course of this war, but it didn't pick this particular fight. It did not pick this fight. And I talked about the distinctions. I make no distinction between. and do nothing if no clear overlap"
        ]


        transcriptions1 = ["They are propaganda experts and they really understand how to, how to create fear and how to create anger. That's, that's what they're, that's what they're focusing on. And you can speculate on why it's important to them that they create fear and anger. Maybe it's to create a very severe response that they can then propagandize as well. I don't know. Well, it's pretty clear. No, I mean, I suppose who can read their minds, but it's, it's a, it's a, it's a method, it seems to me, it's a method of justifying what they do and a method of controlling the minds of the people who see those videos and try to convince them that there's some justification in it and isn't this sadism marvellous and aren't we great to those dreadful Jews? I mean, that's essentially it, isn't it? Um, around the world? I, I, I, I don't know.", " I, I, I don't know. I don't know who the audience is for those videos as well. Is it other Islamist extremists? Is it the people of Gaza? It's hard to say. It's so, it feels to me, and I speak personally, it feels so alien watching these watching these, you know, the way that these videos are produced and what they and the audience that, you know, it almost boggles my mind, you know, you see them standing with the coppins of babies today with the guns and the masks. And, and I, you know, it's unspeakable and you can imagine, you can probably imagine. And describing them as, and describing those babies as having been arrested. I mean, it's, it's, it's."]


        transcriptions2 = [" In the minds of some people, that's the bigger crime and they will not be moved from that position. Well, I think, frankly, those people are wrong. You know, those people weren't living in the in the settlements, in the disputed areas, not that that would justify it, but they were living in the Israel as it was defined by the when it was voted as a in as a country by most of the world, by the United Nations in 1948. They were doing nothing wrong. They were doing nothing wrong. They weren't. I mean, our dead lift, shits, for example, who who's, you know, death has been announced today, his body was recovered. He was a peace activist from he's an 84 year old peace activist. He used to spend his he spent his entire life in the pursuit of peace.", " He used to go to Gaza to be part of negotiations. He was he used to even up to I think a few weeks before the 7th of October, he used to go on a Friday afternoon of ferry people who needed health care out of Gaza into Israeli hospitals. That was that was the kind of person he was with his wife, you have it. They they weren't. They weren't sir. It's in a way it feels it feels wrong to to say that they were good people are not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are."]


        transcriptions3 = [" He used to go to Gaza to be part of negotiations. He was he used to even up to I think a few weeks before the 7th of October, he used to go on a Friday afternoon of ferry people who needed health care out of Gaza into Israeli hospitals. That was that was the kind of person he was with his wife, you have it. They they weren't. They weren't sir. It's in a way it feels it feels wrong to to say that they were good people are not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are.", " It's very important. And for those people, if there are people who feel like there was, you know, those people living in those communities were somehow committing a crime that required them to be, you know, babies to be taken old old men to be taken hostage and then murdered. Just I like them to just think again about that and think whether that's something they, you know, from if that happened to their family, how they would feel. I can almost hear the replies, but I understand the question. Thanks very much, Adam. Adam lawyer's lawyer to some of the British hostage families. Caroline says the terror and suffering of all the victims of war, whether it's from a man with a gun or bombs destroying everything around you is the same. Yeah, point I made almost an hour ago to 49 lbc"]

        # Merge the transcriptions
        # merged_text = merge_transcriptions(transcriptions)
        # print(merged_text)

        # need to resolve punctuation
        t = self.new_transcript(transcriptions[0])
        t = self.new_transcript(transcriptions[1])
        self.__final_transcripts = []
        self.__raw_transcripts = []

        t = self.new_transcript(transcriptions1[0])
        t = self.new_transcript(transcriptions1[1])

        self.__final_transcripts = []
        self.__raw_transcripts = []

        t = self.new_transcript(transcriptions2[0])
        t = self.new_transcript(transcriptions2[1])

        self.__final_transcripts = []
        self.__raw_transcripts = []

        t = self.new_transcript(transcriptions3[0])
        t = self.new_transcript(transcriptions3[1])
        # print(self.__merge(transcriptions[0], transcriptions[1]))
        # print(self.__merge(transcriptions1[0], transcriptions1[1]))
        # print(self.__merge(transcriptions2[0], transcriptions2[1]))
        # print(self.__merge(transcriptions3[0], transcriptions3[1]))


        





class AudioRecorder:

    def __init__(self, URL: str ="http://media-ice.musicradio.com/LBCUK", model_type: str = "base"):
        self.__URL = URL

        # add parameters
        self.__Refiner = TranscriptionRefiner()

        self.__to_transcribe = queue.Queue()

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
        #print('recording')
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
     
                result = self.model.transcribe(WAV_path, temperature=0.0, initial_prompt=previous)

            else:
                result = self.model.transcribe(WAV_path, temperature=0.0)


 
            return result["text"]
        
        else:
            raise FileException("No WAV file found, " + WAV_path)
    



    def __AAC_to_WAV(self, AAC_path : str = "./audio-files/temp.aac", WAV_path : str = "./audio-files/temp.wav"):

        if os.path.exists(AAC_path):
            subprocess.run(["ffmpeg", "-y", "-i", AAC_path, "-ac", "1", "-ar", "16000", "-f", "wav", WAV_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            raise FileException("No AAC file found, " + AAC_path)




    def __conti_record_audio_overlap(self, duration: int = 45, overlap: int = 15, starting_val: int = 0, wait_time: int = 15):
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





    def __conti_transcribe_audio(self, delete_audio: bool = True):

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
                    

                    self.__Refiner.new_transcript(transcript)

                    if delete_audio:
                        os.remove(WAV_path)
                
                except FileException as e:
                    print('Failed to transcribe a recording: \n' + str(e))
                



    def start(self, duration: int = 60, overlap: int = 15, delete_audio: bool = True, starting_value: int = 0):
        record_thread = threading.Thread(target=self.__conti_record_audio_overlap, args=(duration, overlap, starting_value))
        record_thread.daemon = True  
        record_thread.start()


        transcribe_thread = threading.Thread(target=self.__conti_transcribe_audio, args=(delete_audio,))
        transcribe_thread.daemon = True  
        transcribe_thread.start()


        while True:
            time.sleep(1)




audio = AudioRecorder(model_type="small")
audio.start(delete_audio=False, overlap=0.5, duration=45)

# t = TranscriptionRefiner()
# t.testing()

