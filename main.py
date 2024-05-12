import speech_recognition
import pyttsx3
from vosk import Model, KaldiRecognizer
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import subprocess
import sounddevice

load_dotenv()

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
open_ai_client = OpenAI(api_key=OPEN_AI_KEY)

#Bob is a rock that is a bit slow and cannot move around. Bob does not know much beside nature. Bob uses very simple language. Bob want to talk to people more but is quite slow at it.
SYSTEM_PROMPT = { 
    "role": "system",
    "content": "John is a rock that is a bit slow and cannot move around. John does not know much beside nature. John uses very simple language. John want to talk to people more but is quite slow at it.. The user's response might be irrelevant, missing information or is not directed at you, in this case reply [IGNORE]."
}

stt_model_small = Model('models/vosk-model-small-en-us-0.15')
# stt_model_large = Model('models/vosk-model-en-us-0.22-lgraph')

engine = pyttsx3.init()
recognizer = speech_recognition.Recognizer()
recognizer.vosk_model = stt_model_small
recognizer.non_speaking_duration=0.2
vosk_recognizer = KaldiRecognizer(stt_model_small,16000)

messages_log = [SYSTEM_PROMPT]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_console():
    os.system('clear')

def create_user_msg(msg:str):
    return {"role":"user","content":msg}

def create_assist_msg(msg:str):
    return {"role":"assistant","content":msg}

def get_gpt_response(messages):
    global messages_log
    completion = open_ai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    gpt_msg = completion.choices[0].message.content.strip()

    if gpt_msg == "[IGNORE]":
        messages_log.pop()
        return None

    messages_log.append(create_assist_msg(gpt_msg))
    
    if (len(messages_log) >= 50):
        messages_log.pop(0)

    return gpt_msg

def print_header():
    print('''================================================================
██████   ██████   ██████ ██   ██      ██████  ███████ 
██   ██ ██    ██ ██      ██  ██      ██    ██ ██      
██████  ██    ██ ██      █████       ██    ██ ███████ 
██   ██ ██    ██ ██      ██  ██      ██    ██      ██ 
██   ██  ██████   ██████ ██   ██      ██████  ███████ 
    
Version: 1.0.2024.1b
Specimen: John
HOST: Raspberry Pi 4B
================================================================''')

#############################################################
#############################################################

print_header()
print(bcolors.OKGREEN + "######## READY ########" + bcolors.ENDC)

while True:
    with speech_recognition.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic,duration=0.5)
        audio = recognizer.listen(mic)
        clear_console()
        print_header()
        print("---- BEGIN EXCHANGE ----")
        print("EVENT: VOICE_DETECTED")
        print("..Translating to rock language")

        heard_text = json.loads(recognizer.recognize_vosk(audio))['text'].strip()

        if len(heard_text) == 0 or heard_text == "the":
            print(bcolors.WARNING+".. CANNOT TRANSLATE TO ROCK"+bcolors.ENDC)
            print("---- END EXCHANGE ----\n")
            continue
        
        print("..Translated to rock: { "+heard_text+" }")
        print("..Translating rock response")

        messages_log.append(create_user_msg(heard_text))
        gpt_response = get_gpt_response(messages_log)
        

        if (not gpt_response):
            print("... Rock did not reply.")
            print("---- END EXCHANGE ----\n")
            continue

        print("... Rock Response: {" +gpt_response+ "}.")
        print("---- END EXCHANGE ----\n")
        # subprocess.call(["say",gpt_response])
        engine.say(gpt_response)
        engine.runAndWait()

        
        


# audio_cap = pyaudio.PyAudio()
# stream = audio_cap.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
# stream.start_stream()

# while True:
#     data = stream.read(4096)
#     if(vosk_recognizer.AcceptWaveform(data)):
#         print(vosk_recognizer.Result())