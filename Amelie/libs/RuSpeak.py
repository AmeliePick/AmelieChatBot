# -*- coding: utf-8 -*

# === The synthesis module ====

'''
The synthesis is based on gTTS (Google Text-to-Speech). Gets data from a chat file, processes it, and writes it to a file .mp3 for work synthesis need the Internet. 
Due to the algorithm of the library, there is a delay of a few seconds before playback
'''

from random     import randint
from gtts       import gTTS
from time       import sleep
from pydub      import AudioSegment
from libs.AudioManagement import playAudio, _exit



def speak(speech):

    answer = gTTS(text = speech.getOut(), lang = "ru")
    
    #take name of file
    file = "TEMP/sound.mp3"

    #save to .mp3 file
    answer.save(file)

    # Convert mp3 to wav
    sound = AudioSegment.from_mp3(file)
    sound.export("TEMP/sound.wav", format="wav")

    #play sound
    playAudio("TEMP/sound.wav")


    if speech.getNum() == 0:
        _exit("TEMP/sound.wav", file)