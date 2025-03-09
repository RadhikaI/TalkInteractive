import sys
import os

# Add the parent directory (Transcription) to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from transcription import TranscriptProcessor



# Example transcriptions
transcriptions = [
    "who lost three of her limbs, and then there was that little girl, Hind Rajab, a five-year-old Palestinian girl in the Gaza Strip, in a car that had been hit by Israeli missiles as part of this war. All of her relatives in that car were dead. She made a call to an ambulance crew to try and get help. She was in there for days trying to get help and they couldn't get to her, and she died in that situation. Five years of age. Appalling. And as the last, like I said, as the last breath left her body, she experienced that the same way any child who's losing the last breath from their body would experience it. You're not Palestinian or Israeli or Jewish or Muslim.",

    "Jewish or Muslim in those situations. You're a beautiful child taking your last breath. And can we can we try and get to a point where that is where we stand when we talk about this rather than. Yeah, but Israel, yeah, but Palestine, yeah, but Hamas, yeah, but this, yeah, but that. We can have discussions about how we view the actions of Hamas and the Israeli government. I've had many. I'm having one today with you. I think Hamas are unspeakable. I think the Israeli this Israeli government current Israeli government has made dreadful mistakes in the course of this war, but it didn't pick this particular fight. It did not pick this fight. And I talked about the distinctions. I make no distinction between."
]

transcriptions_expected = [["who lost three of her limbs, and then there was that little girl, Hind Rajab, a five-year-old Palestinian girl in the Gaza Strip, in a car that had been hit by Israeli missiles as part of this war. All of her relatives in that car were dead. She made a call to an ambulance crew to try and get help. She was in there for days trying to get help and they couldn't get to her, and she died in that situation. Five years of age. Appalling. And as the last, like I said, as the last breath left her body, she experienced that the same way any child who's losing the last breath from their body would experience it. You're not Palestinian or Israeli or Jewish or Muslim", 
                            
"who lost three of her limbs, and then there was that little girl, Hind Rajab, a five-year-old Palestinian girl in the Gaza Strip, in a car that had been hit by Israeli missiles as part of this war. All of her relatives in that car were dead. She made a call to an ambulance crew to try and get help. She was in there for days trying to get help and they couldn't get to her, and she died in that situation. Five years of age. Appalling. And as the last, like I said, as the last breath left her body, she experienced that the same way any child who's losing the last breath from their body would experience it. You're not Palestinian or Israeli or Jewish or Muslim"], 

["d, as the last breath left her body, she experienced that the same way any child who's losing the last breath from their body would experience it. You're not Palestinian or Israeli or Jewish or Muslim in those situations. You're a beautiful child taking your last breath. And can we can we try and get to a point where that is where we stand when we talk about this rather than. Yeah, but Israel, yeah, but Palestine, yeah, but Hamas, yeah, but this, yeah, but that. We can have discussions about how we view the actions of Hamas and the Israeli government. I've had many. I'm having one today with you. I think Hamas are unspeakable. I think the Israeli this Israeli government current Israeli government has made dreadful mistakes in the course of this war, but it didn't pick this particular fight. It did not pick this fight. And I talked about the distinctions. I make no distinction between",
 
 " in those situations. You're a beautiful child taking your last breath. And can we can we try and get to a point where that is where we stand when we talk about this rather than. Yeah, but Israel, yeah, but Palestine, yeah, but Hamas, yeah, but this, yeah, but that. We can have discussions about how we view the actions of Hamas and the Israeli government. I've had many. I'm having one today with you. I think Hamas are unspeakable. I think the Israeli this Israeli government current Israeli government has made dreadful mistakes in the course of this war, but it didn't pick this particular fight. It did not pick this fight. And I talked about the distinctions. I make no distinction between"
]]


transcriptions1 = ["They are propaganda experts and they really understand how to, how to create fear and how to create anger. That's, that's what they're, that's what they're focusing on. And you can speculate on why it's important to them that they create fear and anger. Maybe it's to create a very severe response that they can then propagandize as well. I don't know. Well, it's pretty clear. No, I mean, I suppose who can read their minds, but it's, it's a, it's a, it's a method, it seems to me, it's a method of justifying what they do and a method of controlling the minds of the people who see those videos and try to convince them that there's some justification in it and isn't this sadism marvellous and aren't we great to those dreadful Jews? I mean, that's essentially it, isn't it? Um, around the world? I, I, I, I don't know.", 

" I, I, I don't know. I don't know who the audience is for those videos as well. Is it other Islamist extremists? Is it the people of Gaza? It's hard to say. It's so, it feels to me, and I speak personally, it feels so alien watching these watching these, you know, the way that these videos are produced and what they and the audience that, you know, it almost boggles my mind, you know, you see them standing with the coppins of babies today with the guns and the masks. And, and I, you know, it's unspeakable and you can imagine, you can probably imagine. And describing them as, and describing those babies as having been arrested. I mean, it's, it's, it's."]

transcriptions1_expected = [[
"They are propaganda experts and they really understand how to, how to create fear and how to create anger. That's, that's what they're, that's what they're focusing on. And you can speculate on why it's important to them that they create fear and anger. Maybe it's to create a very severe response that they can then propagandize as well. I don't know. Well, it's pretty clear. No, I mean, I suppose who can read their minds, but it's, it's a, it's a, it's a method, it seems to me, it's a method of justifying what they do and a method of controlling the minds of the people who see those videos and try to convince them that there's some justification in it and isn't this sadism marvellous and aren't we great to those dreadful Jews? I mean, that's essentially it, isn't it? Um, around the world? I, I, I, I don't know",

"They are propaganda experts and they really understand how to, how to create fear and how to create anger. That's, that's what they're, that's what they're focusing on. And you can speculate on why it's important to them that they create fear and anger. Maybe it's to create a very severe response that they can then propagandize as well. I don't know. Well, it's pretty clear. No, I mean, I suppose who can read their minds, but it's, it's a, it's a, it's a method, it seems to me, it's a method of justifying what they do and a method of controlling the minds of the people who see those videos and try to convince them that there's some justification in it and isn't this sadism marvellous and aren't we great to those dreadful Jews? I mean, that's essentially it, isn't it? Um, around the world? I, I, I, I don't know"],

[" that there's some justification in it and isn't this sadism marvellous and aren't we great to those dreadful Jews? I mean, that's essentially it, isn't it? Um, around the world? I, I, I, I don't know. I don't know who the audience is for those videos as well. Is it other Islamist extremists? Is it the people of Gaza? It's hard to say. It's so, it feels to me, and I speak personally, it feels so alien watching these watching these, you know, the way that these videos are produced and what they and the audience that, you know, it almost boggles my mind, you know, you see them standing with the coppins of babies today with the guns and the masks. And, and I, you know, it's unspeakable and you can imagine, you can probably imagine. And describing them as, and describing those babies as having been arrested. I mean, it's, it's, it's",
 
 ". I don't know who the audience is for those videos as well. Is it other Islamist extremists? Is it the people of Gaza? It's hard to say. It's so, it feels to me, and I speak personally, it feels so alien watching these watching these, you know, the way that these videos are produced and what they and the audience that, you know, it almost boggles my mind, you know, you see them standing with the coppins of babies today with the guns and the masks. And, and I, you know, it's unspeakable and you can imagine, you can probably imagine. And describing them as, and describing those babies as having been arrested. I mean, it's, it's, it's"
]

]


transcriptions2 = [" In the minds of some people, that's the bigger crime and they will not be moved from that position. Well, I think, frankly, those people are wrong. You know, those people weren't living in the in the settlements, in the disputed areas, not that that would justify it, but they were living in the Israel as it was defined by the when it was voted as a in as a country by most of the world, by the United Nations in 1948. They were doing nothing wrong. They were doing nothing wrong. They weren't. I mean, our dead lift, shits, for example, who who's, you know, death has been announced today, his body was recovered. He was a peace activist from he's an 84 year old peace activist. He used to spend his he spent his entire life in the pursuit of peace.", 
                   
" He used to go to Gaza to be part of negotiations. He was he used to even up to I think a few weeks before the 7th of October, he used to go on a Friday afternoon of ferry people who needed health care out of Gaza into Israeli hospitals. That was that was the kind of person he was with his wife, you have it. They they weren't. They weren't sir. It's in a way it feels it feels wrong to to say that they were good people are not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are.",
    
" It's very important. And for those people, if there are people who feel like there was, you know, those people living in those communities were somehow committing a crime that required them to be, you know, babies to be taken old old men to be taken hostage and then murdered. Just I like them to just think again about that and think whether that's something they, you know, from if that happened to their family, how they would feel. I can almost hear the replies, but I understand the question. Thanks very much, Adam. Adam lawyer's lawyer to some of the British hostage families. Caroline says the terror and suffering of all the victims of war, whether it's from a man with a gun or bombs destroying everything around you is the same. Yeah, point I made almost an hour ago to 49 lbc"
    ]

transcriptions2_expected = [[
    " In the minds of some people, that's the bigger crime and they will not be moved from that position. Well, I think, frankly, those people are wrong. You know, those people weren't living in the in the settlements, in the disputed areas, not that that would justify it, but they were living in the Israel as it was defined by the when it was voted as a in as a country by most of the world, by the United Nations in 1948. They were doing nothing wrong. They were doing nothing wrong. They weren't. I mean, our dead lift, shits, for example, who who's, you know, death has been announced today, his body was recovered. He was a peace activist from he's an 84 year old peace activist. He used to spend his he spent his entire life in the pursuit of peace",
    " In the minds of some people, that's the bigger crime and they will not be moved from that position. Well, I think, frankly, those people are wrong. You know, those people weren't living in the in the settlements, in the disputed areas, not that that would justify it, but they were living in the Israel as it was defined by the when it was voted as a in as a country by most of the world, by the United Nations in 1948. They were doing nothing wrong. They were doing nothing wrong. They weren't. I mean, our dead lift, shits, for example, who who's, you know, death has been announced today, his body was recovered. He was a peace activist from he's an 84 year old peace activist. He used to spend his he spent his entire life in the pursuit of peace"
],
["you know, death has been announced today, his body was recovered. He was a peace activist from he's an 84 year old peace activist. He used to spend his he spent his entire life in the pursuit of peace. He used to go to Gaza to be part of negotiations. He was he used to even up to I think a few weeks before the 7th of October, he used to go on a Friday afternoon of ferry people who needed health care out of Gaza into Israeli hospitals. That was that was the kind of person he was with his wife, you have it. They they weren't. They weren't sir. It's in a way it feels it feels wrong to to say that they were good people are not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are",
". He used to go to Gaza to be part of negotiations. He was he used to even up to I think a few weeks before the 7th of October, he used to go on a Friday afternoon of ferry people who needed health care out of Gaza into Israeli hospitals. That was that was the kind of person he was with his wife, you have it. They they weren't. They weren't sir. It's in a way it feels it feels wrong to to say that they were good people are not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are"
],
["not good people because it wouldn't know. No, no person. It's a war crime. It's a war crime, no matter who the person is. But still, it's a it's it's very important. And for those people, if there are people who feel like there was, you know, those people living in those communities were somehow committing a crime that required them to be, you know, babies to be taken old old men to be taken hostage and then murdered. Just I like them to just think again about that and think whether that's something they, you know, from if that happened to their family, how they would feel. I can almost hear the replies, but I understand the question. Thanks very much, Adam. Adam lawyer's lawyer to some of the British hostage families. Caroline says the terror and suffering of all the victims of war, whether it's from a man with a gun or bombs destroying everything around you is the same. Yeah, point I made almost an hour ago to 49 lbc",
 
 " people who feel like there was, you know, those people living in those communities were somehow committing a crime that required them to be, you know, babies to be taken old old men to be taken hostage and then murdered. Just I like them to just think again about that and think whether that's something they, you know, from if that happened to their family, how they would feel. I can almost hear the replies, but I understand the question. Thanks very much, Adam. Adam lawyer's lawyer to some of the British hostage families. Caroline says the terror and suffering of all the victims of war, whether it's from a man with a gun or bombs destroying everything around you is the same. Yeah, point I made almost an hour ago to 49 lbc"

]

]

# Merge the transcriptions
# merged_text = merge_transcriptions(transcriptions)
# print(merged_text)



def test_new_transcript_standard():
    processor0 = TranscriptProcessor()
    (chunk00, non_overlap00) = processor0.new_transcript(transcriptions[0])

    assert chunk00 == transcriptions_expected[0][0]
    assert non_overlap00 == transcriptions_expected[0][1]

    (chunk01, non_overlap01) = processor0.new_transcript(transcriptions[1])

    assert chunk01 == transcriptions_expected[1][0]
    assert non_overlap01 == transcriptions_expected[1][1]

    processor1 = TranscriptProcessor()
    (chunk10, non_overlap10) = processor1.new_transcript(transcriptions1[0])

    assert chunk10 == transcriptions1_expected[0][0]
    assert non_overlap10 == transcriptions1_expected[0][1]

    (chunk11, non_overlap11) = processor1.new_transcript(transcriptions1[1])

    assert chunk11 == transcriptions1_expected[1][0]
    assert non_overlap11 == transcriptions1_expected[1][1]


    processor2 = TranscriptProcessor()
    (chunk20, non_overlap20) = processor2.new_transcript(transcriptions2[0])

    assert chunk20 == transcriptions2_expected[0][0]
    assert non_overlap20 == transcriptions2_expected[0][1]

    (chunk21, non_overlap21) = processor2.new_transcript(transcriptions2[1])

    assert chunk21 == transcriptions2_expected[1][0]
    assert non_overlap21 == transcriptions2_expected[1][1]

    (chunk22, non_overlap22) = processor2.new_transcript(transcriptions2[2])

    assert chunk22 == transcriptions2_expected[2][0]
    assert non_overlap22 == transcriptions2_expected[2][1]



def test_new_transcript_edge():
    processor = TranscriptProcessor()
    (chunk, non_overlap) = processor.new_transcript("")
    assert chunk == ""
    assert non_overlap == ""

    processor = TranscriptProcessor()
    (chunk, non_overlap) = processor.new_transcript("Hellooo, sadfjhfksa?!?!")
    assert chunk == "Hellooo, sadfjhfksa"
    assert non_overlap == "Hellooo, sadfjhfksa"

    (chunk, non_overlap) = processor.new_transcript(" hi!")
    assert chunk == "Hellooo, sadfjhfksa hi"
    assert non_overlap == " hi"

    (chunk, non_overlap) = processor.new_transcript(" HELLLO")
    assert chunk == "Hellooo, sadfjhfksa hi! HELLLO"
    assert non_overlap == "! HELLLO"

    (chunk, non_overlap) = processor.new_transcript(" !HELLLO")
    assert chunk == "Hellooo, sadfjhfksa hi! HELLLO !HELLLO"
    assert non_overlap == " !HELLLO"

    (chunk, non_overlap) = processor.new_transcript("39249")
    assert chunk == "Hellooo, sadfjhfksa hi! HELLLO !HELLLO39249"
    assert non_overlap == "39249"



