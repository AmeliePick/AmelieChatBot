# -*- coding: utf-8 -*-

'''
Chat module for synthesis

The function returns the value from REG in the open_AI (for typing a question) in Ansever (for generating an answer) in SPEC (for articulating an answer)
'''


from modules.Chat_AI import Answer, open_AI
from libs.Recognition import REG, calibration
from libs.Speak import speak
from libs.GoogleSpeak import speak as RUSpeak

def speech():

    return speak(Answer(open_AI(REG())))

def speechRU():
    
    return RUSpeak(Answer(open_AI(REG())))

