# -*- coding: utf-8 -*-

from Singleton             import Singleton

from chat.dialog           import Dialog
from chat.AICore           import Chat

from httpcore._exceptions  import ConnectError

from tools.system          import FileManager
from tools.system          import Network
from tools.logger          import Logger
from tools.input           import voiceInput


from audio.processing      import playAudio, TextToSpeech
from audio.recognition     import SpeechRecognition

from webbrowser            import open as webbrowser_open
from subprocess            import Popen


from re import sub



class Amelie(metaclass = Singleton):
    ''' Bot's logic to get conversation with the user.

    This class is literally bot itself.

    The class is a Singleton.

    '''

    _logger: Logger

    _chat: Chat
    _dialog: Dialog
    _voiceRecorder: SpeechRecognition
    _textToSpeech: TextToSpeech
    _voice: bool

    _programsList:  dict
    _exceptionStack: list
    _parsedInput: list



    def __init__(self, applanguage: str):
        super().__init__()
        self._logger = Logger()

        self._chat = Chat(applanguage)
        self._dialog = Dialog(applanguage)

        # Try to init classes for the voice mode
        self._voice = False
        self._textToSpeech = TextToSpeech()
        try:
            # When voice recorder is initializing, here can be only two exceptions 
            # due to lack of access to the microphone. Until the user resolves 
            # the problems with the microphone, the recorder will be not initialized.
            self._voiceRecorder = SpeechRecognition(self._chat.getLanguage())      
        except OSError:
            self._voiceRecorder = None

        self._programsList = dict()
        self._updateProgramList()

        self._exceptionStack = list()
        self._parsedInput = list()

        return



    def _doAction(self, inputType: str) -> None:
        ''' Do action based on user's request.

        This method must calling in a try block, because the it can generate exceptions.

        '''

        if self._chat.getInputType() == "Exit":
            self._exceptionStack.append(SystemExit(0))

        elif self._chat.getInputType() == "Search":
            url = "https://www.google.ru/search?q="
            webbrowser_open( url + str(self._chat.stemming(self._chat.editInput())), new = 1)

        elif self._chat.getInputType() == "Youtube":
            url = "http://www.youtube.com/results?search_query="
            webbrowser_open( url + str(self._chat.stemming(self._chat.editInput())), new = 1)

        # In this block can be an exception
        elif self._chat.getInputType() == "Open":
                Popen( self.getPathToProgram(self._chat.editInput()) )

        return



    def changeLanguage(self, language: str) -> None:
        self._chat.changeLanguage(language)
        self._dialog.changeLanguage(language)
        self._voiceRecorder.changeLanguage(language)

        return



    def conversation(self, enableVoice: bool, userInput = "") -> str:
        ''' Start the conversation with the bot.
        '''



        def _startChat(userInput: str) -> str:
            chatAnswer = self._chat.launch(userInput)

            try:
                self._doAction(self._chat.getInputType())
            except (FileNotFoundError, OSError):
                exc = FileNotFoundError()
                exc.errno = 1
                self._exceptionStack.append(exc)
                return str(self._dialog.getMessageFor("progNotFound") +
                       " " +
                       self._dialog.getMessageFor("addProg")).replace('\n', '')

            return chatAnswer





        chatAnswer = str()
        try:
            if enableVoice:
                self._setVoice(True)

            if self.getVoice():
                try:
                    userInput = voiceInput()
                except ValueError:
                    userInput = ""

            self._update();
            chatAnswer = _startChat(userInput)



        except FileNotFoundError as exception:
            if exception.errno == 1 and userInput == 'Y' or userInput == 'y':
                self._exceptionStack[0].errno = 2
                chatAnswer = self._dialog.getMessageFor("addProgName") + " " + self._dialog.getMessageFor("addProgPath")

            elif exception.errno == 2:
                parsedInput = userInput.split(" = ")                

                try:
                    if self.getPathToProgram(sub('[\t, \n, \r, \s]', '', parsedInput[0])):
                        chatAnswer = self._dialog.getMessageFor("progNameExist")
                        if(len(parsedInput) == 2):
                            self._parsedInput = parsedInput
                    else: self._exceptionStack[0].errno = 0


                    # Replace program's path
                    if userInput == "R" or userInput == "r":
                        self._programsList[self._parsedInput[0].lower()] = self._parsedInput[1].replace('\n', '')

                        FileManager.clearFile("../DataBase/addedProgramms.db")
                        for key, value in self._programsList.items():
                            FileManager.writeToFile(key + " = " + value + '\n', "../DataBase/addedProgramms.db", 'a')
                        self._exceptionStack[0].errno = 1
                        chatAnswer = _startChat("open " + self._parsedInput[0])
                        self._parsedInput.clear()

                    # Change the name of adding program
                    elif len(parsedInput) == 1 and self._exceptionStack[0].errno == 0: 
                        self._parsedInput[0] = parsedInput[0].lower()

                    if self._exceptionStack[0].errno == 0:
                        self._exceptionStack.pop(0)
                        
                        # this is a crutch to init self._parsedInput when adding a new programm
                        # and the crutch to save self._parsedInput[0] when user change the name of the adding program
                        if len(self._parsedInput) != 2:
                            self._parsedInput = parsedInput

                        self.addProgram(sub('[\t, \n, \r, \s]', '', self._parsedInput[0]), sub('[\t]', '', self._parsedInput[1]).replace("\n", ''))
                        chatAnswer = _startChat("open " + self._parsedInput[0])
                        self._parsedInput.clear()

                except IndexError:
                    chatAnswer = _startChat(userInput)
                    self._parsedInput.clear()
                    self._exceptionStack.pop(0)

            else:
                self._exceptionStack.pop(0)
                self._parsedInput.clear()
                chatAnswer = _startChat(userInput)

        except (ConnectionError, ConnectError):
            self._logger.writeLog()
            self._exceptionStack.pop(0)
            return self._dialog.getMessageFor("serviceError")

        except OSError as e:
            self._logger.writeLog()
            self._exceptionStack.pop(0)
            if e.errno == 6:
                return self._dialog.getMessageFor("errMicroDefine")
            elif e.errno == -9999:
                return self._dialog.getMessageFor("microAccesDenied").replace('\n', " or ") + self._dialog.getMessageFor("errMicroDefine")
            else:
                return self._dialog.getMessageFor("error")            

        except Exception:
            self._logger.logWrite()
            if len(self._exceptionStack) > 0: self._exceptionStack.pop(0)
            return self._dialog.getMessageFor("error")



        if self._voice:
            try:
                self._setVoice(False)
                self.tts(chatAnswer)
            except:
                self._logger.logWrite()
                return str(self._dialog.getMessageFor("serviceError") + chatAnswer)

        return chatAnswer



    def tts(self, pharse: str) -> Exception:
        ''' Convert Text To Speech and play it.
        '''

        self._textToSpeech(pharse, self._chat.getLanguage())
        playAudio("TEMP/sound.wav")

        return



    def _update(self) -> Exception:
        ''' Update the bot's logic.
        '''

        if len(self._exceptionStack) > 0:
            raise self._exceptionStack[0]

        return



    def _updateProgramList(self) -> None:
        programsFile = FileManager.readFile("../DataBase/addedProgramms.db")
        self._programsList.clear()
        for row in programsFile:
            if row != '' and row != '\n' and row != ' ':
                self._programsList.update({row.split(" = ")[0].lower(): row.split(" = ")[1].replace('\n', '')})

        return



    def getPathToProgram(self, programName: str) -> str:
        path = self._programsList.get(programName.lower())
        if path == None:
            return ''
        else:
            return path



    def addProgram(self, program: str, path: str) -> None:
        FileManager.writeToFile(program + " = " + path + '\n', "../DataBase/addedProgramms.db")
        self._updateProgramList()

        return



    def getVoice(self) -> bool:
        return self._voice



    def _setVoice(self, value: bool) -> None:
        if(self._voice == value): return

        if self._voiceRecorder == None:
            # Try to make a late initialization of the voice recorder if it was not initialized in the constructor.
            try:
                self._voiceRecorder = SpeechRecognition(self._chat.getLanguage())
            except OSError as e:
                self._voiceRecorder = None
                e.errno = 6
                self._exceptionStack.append(e)
                return
            
        if value == True and not Network.checkNetworkConnection():
            self._exceptionStack.append(ConnectionError())
            return

        self._voice = value
        return



    def getUserInput(self) -> str:
        return self._chat.getInput()



    def __del__(self):
        pass
