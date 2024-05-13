import sys
import threading
import queue
import sounddevice as sd
import soundfile as sf
import cv2

class AudioRecorder():

    def __init__(self):

        self.open = True
        self.file_name = 'default_name' # This should be replaces with a value given in self.start()
        self.channels = 1
        self.q = queue.Queue()
        
        # Get samplerate
        device_info = sd.query_devices(2, 'input')
        self.samplerate = int(device_info['default_samplerate'])

    def callback(self, indata, frames, time, status):

        # This is called (from a separate thread) for each audio block.
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def record(self):
        with sf.SoundFile(self.file_name, mode='x', samplerate=self.samplerate,
                      channels=self.channels) as file:
            with sd.InputStream(samplerate=self.samplerate,
                                channels=self.channels, callback=self.callback):

                while(self.open == True):
                    file.write(self.q.get())

    def stop(self):
        self.open = False

    def start(self, file_name, file_dir):
        self.open = True
        self.file_name = '{}/{}.wav'.format(file_dir, file_name)
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


class VideoRecorder():
    def __init__(self):
        self.open = True
        self.filename = 'FILENAME'
        self.vid_cap = cv2.VideoCapture(0)
        self.vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
        self.vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        print(fourcc)

        width = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)

        # then use here the actual resolution instead of the hardcoded one
        self.writer = cv2.VideoWriter('recording.avi', fourcc, 24,size,True) 

    def record(self):
        while self.open == True:
            _, frame = self.vid_cap.read()
            self.writer.write(frame)
    
    def stop(self):
        self.open = False
        self.vid_cap.release()
        self.writer.release()

    def start(self):
        self.open = True
        video_thread = threading.Thread(target=self.record)
        video_thread.start()