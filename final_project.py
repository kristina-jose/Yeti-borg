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
timeForward1m = 2.264260905861877                   # Number of seconds needed to move about 1 meter
timeBackward1m = 3.4834783167105794
timeSpin360_left = 1.8037625234370742                     # Number of seconds needed to make a full left / right spin
timeSpin360_right = 1.8438461350690094                     # Number of seconds needed to make a full left / right spin
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
        # Calculate the required time delay
        numSeconds = (-angle / 360.0) * timeSpin360_left
    else:
        # Right turn
        driveLeft  = +1.0
        driveRight = -1.0
        # Calculate the required time delay
        numSeconds = (angle / 360.0) * timeSpin360_right

    # Perform the motion
    PerformMove(driveLeft, driveRight, numSeconds)

# Function to drive a distance in meters
def PerformDrive(meters):
    if meters < 0.0:
        # Reverse drive
        driveLeft  = -1.0
        driveRight = -1.0
        meters *= -1
        numSeconds = meters * timeBackward1m
    else:
        # Forward drive
        driveLeft  = +1.0
        driveRight = +0.980
        numSeconds = meters * timeForward1m
    # Calculate the required time delay
    #numSeconds = meters * timeForward1m
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
    print("started")
    result = yolo_client.main(image=frame)
    print("ended")   
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
    object1 = get_object(mock=False) #object1 will give a dictionary with the distance
    print(object1)
    return object1

def find_cup(color):
    while True:
        target = 0
        objects = looking_for_object()
        if len(objects):
            for obj in objects:
                if obj.get("color") == color:
                    box = obj.get("box")
                    target = (obj.get("distance") / 100)
                    x, y, width, height = box[0], box[1], box[2], box[3]
                    return target, x, width
                else:
                    trying_to_find_last_cup(color)
        else:
            trying_to_find_last_cup(color)

def trying_to_find_last_cup(color):
    x = 0
    for i in range(1, 100):
        PerformSpin(x)
        objects = looking_for_object()
        for obj in objects:
            if obj.get("color") == color:
                return 
        
        if x > 0:
            x = -(25*i)
            
        else:
            x = 25*i

def correct_angle(target, x, width, color):
    while True:
        if target < 0.5:
            target += 1.5
            PerformDrive(target)
        else:
            middle = x + (width / 2)
            if 290 < middle < 350:
                target += 1.5
                PerformDrive(target)
                return
            elif middle < 290:
                PerformSpin(-90)
                time.sleep(1)
                PerformDrive(0.03)
                time.sleep(1)
                PerformSpin(90)
            else:
                PerformSpin(90)
                time.sleep(1)
                PerformDrive(0.03)
                time.sleep(1)
                PerformSpin(-90)
            target, x, width = find_cup(color)
    
def final_project():
    colors = ["BLUE", "GREEN", "RED"]
    for color in colors:
        target, x, width = find_cup(color)
        correct_angle(target, x, width, color)
        PerformDrive(-0.2)
        time.sleep(1)
        PerformSpin(180)

def calibrating():
    global timeSpin360_left
    global timeSpin360_right
    test_length = float(input("Enter angle it calibrate for the left side "))
    PerformSpin(test_length)
        
    move_length = float(input("Enter angle robit moved for the left side "))
    if test_length != move_length:
        timeSpin360_left = (test_length/move_length)*timeSpin360_left
        print(timeSpin360_left)

    test_length = float(input("Enter angle it calibrate for the right side "))
    PerformSpin(test_length)
        
    move_length = float(input("Enter angle robit moved for the right side "))
    if test_length != move_length:
        timeSpin360_right = (test_length/move_length)*timeSpin360_right
        print(timeSpin360_right)


def calibrating_meters():
    global timeForward1m
    test_length = float(input("Enter the distance you want to move "))
    PerformDrive(test_length)
    
    move_length = float(input("Actually distance you moved "))
    if test_length != move_length:
        timeForward1m = (test_length/move_length)*timeForward1m
        print(timeForward1m)


if __name__ == '__main__':
    done = False

    while not done:
        option = int(input("Press a number "))
        if option == 0:
            "calibrating"
            calibrating()            
        elif option == 1:
            "movement"               
            calibrating_meters()
        elif option == 2:
            "Challange final project"
            final_project()
        else:
            done = True
        

print("exit")
