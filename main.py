import speech_recognition
import pyttsx3
import time
from speech_recognition import AudioData, Recognizer
from vosk import Model, KaldiRecognizer
import pyaudio
import json

stt_model_small = Model('models/vosk-model-small-en-us-0.15')
stt_model_large = Model('models/vosk-model-en-us-0.22-lgraph')

engine = pyttsx3.init()
recognizer = speech_recognition.Recognizer()
recognizer.vosk_model = stt_model_large
recognizer.non_speaking_duration=0.2
vosk_recognizer = KaldiRecognizer(stt_model_small,16000)

# default_microphone = speech_recognition.Microphone()
# def on_speech(recognizer:Recognizer, audio_data:AudioData):
#     print("listening")
#     text = recognizer.recognize_vosk(audio_data)
# recognizer.listen_in_background(default_microphone,callback=on_speech)

while True:
    with speech_recognition.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic,duration=0.2)
        audio = recognizer.listen(mic)
        print("..Start processing audio")
        text = json.loads(recognizer.recognize_vosk(audio))['text']
        print(text)


# audio_cap = pyaudio.PyAudio()
# stream = audio_cap.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
# stream.start_stream()

# while True:
#     data = stream.read(4096)
#     if(vosk_recognizer.AcceptWaveform(data)):
#         print(vosk_recognizer.Result())
    


engine.say("I will speak this text")
engine.runAndWait()