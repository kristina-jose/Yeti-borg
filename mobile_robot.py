# Standard imports
from __future__ import division
import sys,tty,termios,os
import time
import math
import cv2
import numpy as np
import keyboard
from yolo import detect_objects
import yolo_client
from picamera.array import PiRGBArray
from picamera import PiCamera
import random

import ZeroBorg3 as ZeroBorg

# Camera settings
width = 640/2
height = 480/2
frameRate = 32

# Initializing the camera
#camera = PiCamera()
#camera.awb_mode = 'auto'
#camera.resolution = (int(width), int(height))
#camera.framerate = frameRate
#rawCapture = PiRGBArray(camera, size=(int(width), int(height)))
#time.sleep(0.1)


# Settings

# Color setting for the mask

hueLow = 0
saturationLow = 88
valueLow = 75

hueHigh = 11
saturationHigh = 255
valueHigh = 251

# Toggles for debuging
displayWindows = False
ready = False

# Variables
xPos = 0;
steerMultiplier = 0.8

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                   # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print ('No ZeroBorg found, check you are attached :)')
    else:
        print ('No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress))
        for board in boards:
            print ('    %02X (%d)' % (board, board))
        print ('If you need to change the IC address change the setup line so it is correct, e.g.')
        print ('ZB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
#ZB.SetEpoIgnore(True)                  # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)              # Disable the communications failsafe
ZB.ResetEpo()

# Movement settings (worked out from our YetiBorg v2 on a smooth surface)
timeForward1m = 2.3                     # Number of seconds needed to move about 1 meter
timeSpin360   = 2.245                     # Number of seconds needed to make a full left / right spin
#timeSpin360 = global(timeSpin360)
testMode = False                        # True to run the motion tests, False to run the normal sequence

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Function to perform a general movement
def PerformMove(driveLeft, driveRight, numSeconds):
    # Set the motors running
    ZB.SetMotor1(-driveRight * maxPower) # Rear right
    ZB.SetMotor2(-driveRight * maxPower) # Front right
    ZB.SetMotor3(-driveLeft  * maxPower) # Front left
    ZB.SetMotor4(-driveLeft  * maxPower) # Rear left
    # Wait for the time
    time.sleep(numSeconds)
    # Turn the motors off
    ZB.MotorsOff()

# Function to spin an angle in degrees
def PerformSpin(angle):
    if angle < 0.0:
        # Left turn
        driveLeft  = -1.0
        driveRight = +1.0
        angle *= -1
    else:
        # Right turn
        driveLeft  = +1.0
        driveRight = -1.0
    # Calculate the required time delay
    numSeconds = (angle / 360.0) * timeSpin360
    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)

# Function to drive a distance in meters
def PerformDrive(meters):
    if meters < 0.0:
        # Reverse drive
        driveLeft  = -1.0
        driveRight = -1.0
        meters *= -1
    else:
        # Forward drive
        driveLeft  = +1.0
        driveRight = +1.0
    # Calculate the required time delay
    numSeconds = meters * timeForward1m
    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)

# Function to drive fullspeed with turn options -> slowdown a side
def Drive(right,left):
    ZB.SetMotor1(-maxPower + right) # Rear right
    ZB.SetMotor2(-maxPower + right) # Front right
    ZB.SetMotor3(-maxPower + left) # Front left
    ZB.SetMotor4(-maxPower + left) # Rear left

class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


def get_object(mock=False):
    if mock:
        return [{"label":"mock", "distance": 260, "box":None}]
    # Set up the Raspberry Pi camera module
    camera = cv2.VideoCapture(0)
    #camera.set(3, 640) # set video width
    #camera.set(4, 480) # set video height
    ret, frame = camera.read()
    camera.release()
    # rotate the image
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    cv2.imwrite("camera_test.jpg", frame)
    # result = detect_objects(frame, result_image=True, calibrate=True)
    result = yolo_client.main(image=frame, final_project=False)
    return result

def move_around():
    PerformSpin(90)
    time.sleep(1)
    PerformDrive(0.20)
    time.sleep(1)
    PerformSpin(-80)
    time.sleep(1)
    PerformDrive(0.50)
    time.sleep(1)
    PerformSpin(-80)
    time.sleep(1)
    PerformDrive(0.12)
    time.sleep(1)
    PerformSpin(90)
    time.sleep(1)

def looking_for_object():
    distance = []
    box = []
    target = 0
    object1 = get_object(mock=False) #object1 will give a dictionary with the distance
    print(object1)
    short_dis = 300
    for objects in object1:
        distance.append(objects.get("distance"))
        if objects.get("distance") < short_dis:
            box = objects.get("box")
            short_dis = objects.get("distance")
            
    short_dis = (short_dis / 100)
    return short_dis, box

def correct_angle():
    target, box = looking_for_object()
    target += 0.10
    if len(box):
        x, y, width, height = box[0], box[1], box[2], box[3]
    else:
        challange3()
        return
    frame_width = 640
    middle = x + (width / 2)
    if 250 < middle < 390:
        PerformDrive(target)
    elif middle < 290:
        PerformSpin(-10)
        correct_angle()
    else:
        PerformSpin(10)
        correct_angle() 

def calibrating():
    global timeSpin360
    test_length = float(input("Enter angle it calibrate in meters "))
    PerformSpin(test_length)
    
    move_length = float(input("Enter angle robit moved in meters "))
    if test_length != move_length:
        timeSpin360 = (test_length/move_length)*timeSpin360

def challange1():
    distance = []
    target = 0
    object1 = get_object(mock=False) #object1 will give a dictionary with the distance
    print(object1)
    for objects in object1:
        distance.append(objects.get("distance"))         
        target = min(distance)
    target = (target / 100) - 0.05 
    PerformDrive(target)    

def challange2():
    distance = []
    target = 0
    object1 = get_object(mock=False) #object1 will give a dictionary with the distance
    print(object1)
    for objects in object1:
        distance.append(objects.get("distance"))         
        target = min(distance)
    target = (target / 100) - 0.10 
    PerformDrive(target)
    move_around()
    target2 = 2 - target - 0.4
    PerformDrive(target2)
    
def challange3():
    target, box = looking_for_object()       
    if target > 2.5:
        PerformSpin(45)
        target, box = looking_for_object()
        if target > 2.5:
            PerformSpin(45)
            target, box = looking_for_object()
            if target > 2.5:
                PerformSpin(-90)
                PerformDrive(0.20) 
                challange3()
            else:
                correct_angle()  
        else:
            correct_angle()
    else:
        correct_angle()

        
        
if __name__ == '__main__':

    done = False

    while not done:
        option = int(input("Press a number "))
        if option == 0:
            "calibrating"
            calibrating()
        elif option == 1:
            "Challange 1"
            challange1()

        elif option == 2:
            "Challange 2"
            challange2()

        elif option == 3:
            "Challange 3"               
            challange3()

        else:
            done = True
        

print("exit")
