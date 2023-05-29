import requests
import cv2
import json

def main(**args):
    # make a request to the server
    image = args["image"]

    request_json = json.dumps({"image": image.tolist()})
    
    # convert the image to base64 format and send it to the server
    image = cv2.imencode(".jpg", image)[1].tobytes()

    result = requests.post("https://6a62-145-118-234-145.ngrok-free.app/yolo", files={"image": image}).json()

    return result