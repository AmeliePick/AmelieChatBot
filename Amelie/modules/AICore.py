# -*- coding: utf-8 -*-

'''
Chat is a neural network that classifies requests from the user. 
Then, after processing the type of the question, it passes it to the answer function, 
where the answer is processed and the operations are performed according to the input.

User input is also processed for search engines. Unnecessary part of the phrase is cut off and search is performed only within the meaning of the sentence.

'''

from numpy          import random, arange
from pickle         import dump, load

from sklearn.feature_extraction.text    import TfidfVectorizer
from sklearn.linear_model               import SGDClassifier
from sklearn.pipeline                   import Pipeline

from .AIFiles   import dataSet, checkLang

class Chat:
    input_ = ""
    inputType_ = ""
    sessionInput_ = {}


    def getInput(self) -> str:
        return self.input_


    def getInputType(self) -> str:
        return self.inputType_

    def getSessionInput(self) -> dict:
        return self.sessionInput_


    '''
    Functions for creating and training the neural network to recognize the type of input. 
    For example: What is the weather today? - Weather. Where is Paris? - Location

    '''
    def AI(self) -> dict:
        global dataSet

        Edit = {'text': [], 'tag':[]}
        for line in dataSet:
            if(line == '' or line == '\n' or line == ' '):
                continue

            row = line.split(' @ ')
            
            
            Edit['text'] += [row[0]]
            Edit['tag'] += [row[1]]
    
        
        return Edit


    def training(self, Edit, Val_split = 0.1) -> dict:
        global checkLang

        lenght = len(Edit['text'])
        indexes = arange(lenght)
        random.shuffle(indexes)

        X = [Edit['text'][i]
        for i in indexes ]
        Y = [Edit['tag'][i]
        for i in indexes]

        nb_valid_samples = int(Val_split * lenght)


        #save the model to disk
        filename = 'modelEN.sav'
        if checkLang == "RU":
            filename = 'model.sav'
        dump(nb_valid_samples, open("models/"+filename, 'wb'))
    
        #load the model from disk
        loaded_model = load(open("models/"+filename, 'rb'))
  

        return { 
            'train': { 'x': X[:-loaded_model], 'y': Y[:-loaded_model]  },
            'test': { 'x': X[-loaded_model:], 'y': Y[-loaded_model:]  }
        }


    def Enter(self, voice: str = "") -> None:
        while(True):
            if(voice == ""):
                self.input_ = str(input('\n---> '))
                if self.input_ == '' or self.input_ == '\n' or self.input_ == ' ':
                    continue
                else:
                    break
            else:
                self.input_ = voice
                break


    def open_AI(self) -> None:
        data = self.AI()
        D = self.training(data)
        text_clf = Pipeline([
                        ('tfidf', TfidfVectorizer()),
                        ('clf', SGDClassifier(loss='hinge')),
                        ])
        text_clf.fit(D['train']['x'], D['train']['y'])
        predicted = text_clf.predict( D['test']['x'] )

        #give a type of input
        input = []
        input.append(self.input_.capitalize())


        try:
            pred = text_clf.predict(input)
        except:
            return "Pause"
        
        self.inputType_ = ''.join(pred).replace('\n', '')

        self.sessionInput_[self.input_] = self.inputType_
