#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import io
import threading
import picamera

global flag
flag=1
class Camera(object):
    global flag
    thread = None  
    frame = None  
    last_access = 0  
    def initialize(self):
        if Camera.thread is None:
            
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame
    def Close(self):
        global flag
        flag=0

        
    @classmethod
    def _thread(cls):
        global flag   
        with picamera.PiCamera() as camera:
           
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True

           
            camera.start_preview()
            time.sleep(1)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                use_video_port=True):
               
                stream.seek(0)
                cls.frame = stream.read()

                
                stream.seek(0)
                stream.truncate()

                
                if time.time() - cls.last_access > 1 :
                    break
                if flag==0:
                    camera.close()
                    # camera.resolution = (1024,768)#摄像界面为1024*768
                    # camera.start_preview()#开始摄像
                    # time.sleep(1)
                    # camera.capture('faceimage.jpg')#拍照并保存
                    # time.sleep(1)
                    # flag=1
        cls.thread = None
    
def Start():
        global flag
        flag=1
        Camera._thread()