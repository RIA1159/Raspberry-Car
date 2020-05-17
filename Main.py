#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep
import RPi.GPIO as GPIO 
import pigpio
import time
from flask import Flask, render_template, request, Response
from camera_pi import Camera
from picamera import PiCamera
import camera_pi
import threading
import sys
import random

app = Flask(__name__)

global panServoAngle
global tiltServoAngle
global flag
global xmotor
global ymotor
global flag1
global derail
derail=0
xmin=-30
xmax=150
ymin=-20
ymax=90
xmotor=60
ymotor=-20
movestep=10
flag=1
flag1=1
panServoAngle = 90
tiltServoAngle = 90
panPin = 17
tiltPin = 18

@app.route('/')
def index():
    """Video streaming home page."""

    return render_template('index.html')

def gen(camera):
    global flag
    """Video streaming generator function."""
    while flag==1:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



def setmotor(servo,angle):
    if servo==17:
        os.system('sudo python3 angleServoCtrl.py ' + str(servo) + " " + str(angle))
    elif servo==18:
        os.system('sudo python3 angleServoCtrl.py ' + str(servo) + " " + str(angle))
    
@app.route("/panup")
def panup():
    global ymotor
    if ymotor+movestep<=ymax:
        ymotor=ymotor+movestep
        setmotor(tiltPin,ymotor)
    return render_template("index.html")

@app.route("/pandown")
def pandown():
    global ymotor
    if ymotor-movestep>=ymin:
        ymotor=ymotor-movestep
        setmotor(tiltPin,ymotor)
    return render_template("index.html")
@app.route("/panleft")
def panleft():
    global xmotor
    if xmotor+movestep<=xmax:
        xmotor=xmotor+movestep
        setmotor(panPin,xmotor)
    return render_template("index.html")
@app.route("/panright")
def panright():
    global xmotor
    if xmotor-movestep>=xmin:
        xmotor=xmotor-movestep
        setmotor(panPin,xmotor)
    return render_template("index.html")
@app.route("/panpause")
def panpaues():
    return render_template("index.html")

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7,GPIO.OUT)
    GPIO.setup(11,GPIO.OUT)
    GPIO.setup(13,GPIO.OUT)
    GPIO.setup(15,GPIO.OUT)
def gobackward(tf=3):
    init()
    GPIO.output(7,0)
    GPIO.output(11,1)
    GPIO.output(13,1)
    GPIO.output(15,0)
    time.sleep(tf)
    GPIO.cleanup()
def goforward(tf=3):
    init()
    GPIO.output(7,1)
    GPIO.output(11,0)
    GPIO.output(13,0)
    GPIO.output(15,1)
    time.sleep(tf)
    GPIO.cleanup()
def goleft(tf=0.5):
    init()
    GPIO.output(7,1)
    GPIO.output(11,0)
    GPIO.output(13,1)
    GPIO.output(15,0)
    time.sleep(tf)
    GPIO.cleanup()
def goright(tf=0.5):
    init()
    GPIO.output(7,0)
    GPIO.output(11,1)
    GPIO.output(13,0)
    GPIO.output(15,1)
    time.sleep(tf)
    GPIO.cleanup()
def distance(measure='cm'):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12,GPIO.OUT)
        GPIO.setup(16,GPIO.IN)
        GPIO.output(12,True)
        time.sleep(0.000015)
        GPIO.output(12,False)
        while GPIO.input(16) == 0:
            noisg = time.time()
        while GPIO.input(16) == 1:
            sig = time.time()
        tl=sig - noisg
        if measure == 'cm':
            distance = tl/0.000058
        elif measure == 'in':
            distance = tl/0.000148
        else:
            print("improper choice of measure: in or cm")
            distance = None

        GPIO.cleanup()
        return distance
    except:
        distance = 100
        GPIO.cleanup()
        return distance

def check_front():
    init()
    dist = distance()

    if dist < 20:
        init()
        gobackward(2)
        dist = distance()
        if dist < 20:
            init()
            goleft(0.5)
            init()
            gobackward(2)
            dist = distance()
            if dist < 20:
                sys.exit

@app.route("/backward")
def backward():
    gobackward(3)
    return render_template("index.html")
@app.route("/forward")
def forward():
    goforward(3)
    return render_template("index.html")
@app.route("/left")
def left():
    goleft(0.5)
    return render_template("index.html")
@app.route("/right")
def right():
    goright(0.5)
    return render_template("index.html")
def autonomy():
    global derail
    derail=1
    while derail == 1:
        tf = 0.060
        x = random.randrange(0,3)

        if x == 0:
            for y in range(50):
                check_front()
                goforward(tf)
        elif x == 1:
            goleft(0.5)
            for y in range(50):
                check_front()
                goforward(tf)
        elif x == 2:
            goright(0.5)
            for y in range(50):
                check_front()
                goforward(tf)
        
        time.sleep(0.5)
    return render_template("index.html")
@app.route("/shutdownrun")
def shutdownrun():
    global derail
    derail = 0
    return render_template("index.html")


def getimage():
    camera = PiCamera()
    camera.resolution = (1024,768)#摄像界面为1024*768
    camera.start_preview()#开始摄像
    time.sleep(1)
    camera.capture('faceimage.jpg')#拍照并保存
    time.sleep(1)
    camera.close()


@app.route("/startre")
def startre():
    global flag
    global flag1
    while True:
        time.sleep(40)
        flag=0
        time.sleep(2)
        getimage()
        time.sleep(1)
        flag=1
        os.system("sudo python3 recognition.py")
        if flag1==0:
            flag1=1
            return render_template("index.html")
    return render_template("index.html")
@app.route("/stopre")
def stopre():
    global flag
    global flag1
    flag=1
    flag1=0
    return render_template("index.html")




if __name__ == '__main__':
    setmotor(tiltPin,ymotor)
    setmotor(panPin,xmotor)
    app.run(host='0.0.0.0', port =80, debug=True, threaded=True)
    
    
    