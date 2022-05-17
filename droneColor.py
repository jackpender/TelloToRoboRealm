#Import necessary libraries
from flask import Flask, render_template, Response
from waitress import serve
import cv2, time
from datetime import datetime
import argparse
import os

from djitellopy import Tello

import numpy as np

#Initialize the Flask app
app = Flask(__name__)

#Image Settings
width = 320
height = 240
startCounter = 1 #0 for flight, 1 for testing

#Connect to Tello Drone
me = Tello()
# me.connect()
# me.for_back_velocity = 0
# me.left_right_velocity = 0
# me.up_down_velocity = 0
# me.yaw_velocity = 0
# me.speed = 0

# print(me.get_battery())

# me.streamoff()
# me.streamon()

# me.disconnect()

camera = cv2.VideoCapture(0)

def gen_frames():
    first_frame=None
    while True:
        frame_read = me.get_frame_read()
        myFrame = frame_read.frame
        img = cv2.flip(myFrame, 1)
        # img = cv2.GaussianBlur(img,(7,7),0)

        # success, myFrame = frame_read.frame
        # success, frame = camera.read()  # read the camera frame
        # myFrame = cv2.flip(myFrame, 1)



        #converting frame(img) from BGR (Blue-Green-Red) to HSV (hue-saturation-value)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        #defining the range of Yellow color
        yellow_lower = np.array([34,97,35])
        yellow_upper = np.array([154,255,157])

        #finding the range yellow colour in the image
        yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

        #Morphological transformation, Dilation         
        kernal = np.ones((5 ,5), "uint8")

        blue=cv2.dilate(yellow, kernal)

        res=cv2.bitwise_and(img, img, mask = yellow)

        #Tracking Colour (Yellow) 
        (contours,hierarchy)=cv2.findContours(yellow,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        for pic, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if(area>300):
                        
                        x,y,w,h = cv2.boundingRect(contour)     
                        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)


        (flag, encodedImage) = cv2.imencode(".jpg", img)

        if not flag:
            continue
        
        # if not success:
        #     break
        # else:
        #     ret, buffer = cv2.imencode('.jpg', myFrame)
        #     myFrame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')  ###concat frame one by one and show result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

serve(app,host='0.0.0.0',port=80) ###Deploys flask app using waitress

# me.disconnect()