import pyttsx3
import subprocess
import pyaudio
import recorder
import time
import sounddevice as sd

# print("1")
# subprocess.call(["say","Hello World! (MESSAGE)"])
# print("2")

# po = pyaudio.PyAudio()
# for index in range(po.get_device_count()): 
#     desc = po.get_device_info_by_index(index)
#     if desc["name"] == "record":
#         print ("DEVICE: %s  INDEX:  %s  RATE:  %s " %  (desc["name"], index,  int(desc["defaultSampleRate"])))

print(sd.query_devices())
# recorder = recorder.Recorder("/Users/futianzhou/Documents/Projects/des242-A3/interaction_logs")
# recorder.start()
# engine = pyttsx3.init()
# engine.say("hello, this is a test.")
# engine.runAndWait()
# recorder.stop()

from gpiozero import Button
from time import sleep

button = Button(17)
print("waiting")
button.wait_for_active()
while button.active_time:
    sound_recorded = sd.rec(1)
button.wait_for_inactive()
sd.stop()
sd.play(sound_recorded)

while True:
    if button.is_pressed:
        print("Pressed")
    else:
        print("Released")
    sleep(1)


