import pyttsx3
import subprocess
import pyaudio
# print("1")
# subprocess.call(["say","Hello World! (MESSAGE)"])
# print("2")

po = pyaudio.PyAudio()
for index in range(po.get_device_count()): 
    desc = po.get_device_info_by_index(index)
    if desc["name"] == "record":
        print ("DEVICE: %s  INDEX:  %s  RATE:  %s " %  (desc["name"], index,  int(desc["defaultSampleRate"])))

# engine = pyttsx3.init()
# engine.say("hello, this is a test. My name is John. John is rock. Rock cannot move.")
# engine.runAndWait()
