import speech_recognition
import pyttsx3
from vosk import Model, KaldiRecognizer
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import subprocess
import sounddevice
import io
import wave
from datetime import datetime
import threading
import cv2
import recorder

load_dotenv()

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
open_ai_client = OpenAI(api_key=OPEN_AI_KEY)
#Bob is a rock that is a bit slow and cannot move around. Bob does not know much beside nature. Bob uses very simple language. Bob want to talk to people more but is quite slow at it.
SYSTEM_PROMPT = { 
    "role": "system",
    "content": "John is a rock that is a bit slow and cannot move around. John does not know much beside nature. John uses very simple language. John want to talk to people more but is quite slow at it.. The user's response might be irrelevant, missing information or is not directed at you, in this case reply [IGNORE]."
}
# stt_model_small = Model('models/vosk-model-small-en-us-0.15')
engine = pyttsx3.init()
recognizer = speech_recognition.Recognizer()
# recognizer.vosk_model = stt_model_small
recognizer.non_speaking_duration=0.2
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
================================================================
''')

############ RECORDING UTILITY ####################

interaction_recorder = None
recording_stopper = None

def stop_recording():
    global interaction_recorder
    global recording_stopper
    interaction_recorder.stop()
    interaction_recorder = None
    recording_stopper = None

#############################################################
#############################################################

clear_console()
print_header()
print(bcolors.OKGREEN + "######## READY ########" + bcolors.ENDC)
# threading.Timer(10,lambda:interaction_recorder.stop())


with speech_recognition.Microphone() as mic:
    
    while True:
        recognizer.adjust_for_ambient_noise(mic,duration=1)
        try:
            audio = recognizer.listen(mic,timeout=1,phrase_time_limit=7)
        except speech_recognition.WaitTimeoutError:
            speech_waiting_cnt = 0
            continue
        clear_console()
        print_header()
        print("EVENT: VOICE_DETECTED")
        print("..Translating to rock language")

        wav_bytes = audio.get_wav_data(convert_width=1)
        # heard_text = json.loads(recognizer.recognize_vosk(audio))['text'].strip()
        heard_text = open_ai_client.audio.transcriptions.create(file=("why.wav",audio.get_wav_data(convert_width=1)),language="en",model="whisper-1",response_format="text").strip()

        if len(heard_text) == 0 or heard_text == "the":
            print(bcolors.WARNING+".. CANNOT TRANSLATE TO ROCK"+bcolors.ENDC)
            continue
        
        print("..Translated to rock: { "+heard_text+" }")
        print("..Translating rock response")

        messages_log.append(create_user_msg(heard_text))
        gpt_response = get_gpt_response(messages_log)
        

        if (not gpt_response):
            print(bcolors.WARNING+"..Rock did not reply."+bcolors.ENDC)
            continue
        
        print(bcolors.OKGREEN +"..Translation Successful."+bcolors.ENDC)
        print("Response: {" +gpt_response+ "}.")

        with open("conversation_log.txt",mode='a') as log_file:
            log_file.write("["+datetime.now().isoformat(timespec="seconds")+"]"+"User: "+heard_text+"\n")
            log_file.write("["+datetime.now().isoformat(timespec="seconds")+"]"+"Rock: "+gpt_response+"\n")

        # if not recording, start
        if not interaction_recorder:
            interaction_recorder = recorder.Recorder("/Users/futianzhou/Documents/Projects/des242-A3/interaction_logs")
            recording_stopper = threading.Timer(15,stop_recording)
            recording_stopper.start()
        else:
            recording_stopper.cancel()
            recording_stopper = threading.Timer(15,stop_recording)
            recording_stopper.start()
        
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