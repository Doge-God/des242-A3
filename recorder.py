import sys
import threading
import queue
import sounddevice as sd
import soundfile as sf
import cv2
from datetime import datetime
import os
import time

class AudioRecorder():

    def __init__(self,file_name):

        self.open = True
        self.file_name = file_name
        self.channels = 2
        self.q = queue.Queue()
        
        # Get samplerate
        device_info = sd.query_devices(3, 'input')
        self.samplerate = int(device_info['default_samplerate'])
        print(device_info)

    def callback(self, indata, frames, time, status):

        # This is called (from a separate thread) for each audio block.
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def record(self):
        with sf.SoundFile(self.file_name, mode='x', samplerate=self.samplerate,
                      channels=self.channels) as file:
            with sd.InputStream(device=3,samplerate=self.samplerate,
                                channels=self.channels, callback=self.callback):

                while(self.open == True):
                    file.write(self.q.get())

    def stop(self):
        self.open = False
        time.sleep(0.5)

    def start(self):
        self.open = True
        self.file_name = '{}.wav'.format(self.file_name)
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

class AudioRecorder2():
    def __init__(self,file_name):
        self.open = True
        self.file_name = file_name
        self.channels = 2
        self.q = queue.Queue()
        
        # Get samplerate
        device_info = sd.query_devices(3, 'input')
        self.samplerate = int(device_info['default_samplerate'])
    pass

class VideoRecorder():
    def __init__(self,filename):
        self.open = True
        self.filename = filename
        self.vid_cap = cv2.VideoCapture(0)
        self.vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
        self.vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        width = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)

        # then use here the actual resolution instead of the hardcoded one
        # print(filename+".avi")
        self.writer = cv2.VideoWriter("{fn}.avi".format(fn=self.filename), fourcc, 24,size,True) 

    def record(self):
        while self.open == True:
            _, frame = self.vid_cap.read()
            self.writer.write(frame)
    
    def stop(self):
        self.open = False
        time.sleep(0.5)
        self.vid_cap.release()
        self.writer.release()

    def start(self):
        self.open = True
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

class Recorder():
    def __init__(self,interaction_log_path:str):
        self.log_time_id = datetime.now().strftime("%a|%m-%d-%H:%M:%S")

        self.video_recorder = VideoRecorder("./interaction_logs/"+self.log_time_id)
        self.audio_recorder = AudioRecorder("./interaction_logs/"+self.log_time_id)
    
    def start(self):
        self.video_recorder.start()
        self.audio_recorder.start()

    def stop(self):
        self.video_recorder.stop()
        self.audio_recorder.stop()