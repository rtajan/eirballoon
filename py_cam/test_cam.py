#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#

# Title: test_cam.py

import cv2
import imutils
import time

cap = cv2.VideoCapture(1)
ret, frame = cap.read()

def takePicture():
    (grabbed, frame) = cap.read()
    showimg = frame
    cv2.imshow('img1', showimg)  # display the captured image
    cv2.waitKey(1)
    time.sleep(0.3) # Wait 300 miliseconds
    image = 'capture.png'
    cv2.imwrite(image, frame)
    cap.release()
    return image

print(takePicture())
