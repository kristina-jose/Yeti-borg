import cv2
import numpy as np
import time
import json

# Set up the Raspberry Pi camera module
camera = cv2.VideoCapture(0)
camera.set(3, 640) # set video width
camera.set(4, 480) # set video height

ret, frame = camera.read()

cv2.imwrite("camera_test.jpg", frame)


result = detect_objects(frame, result_image=True)

with open("yolo_result.json", "w") as f:
    f.write(json.dumps(result))

# result