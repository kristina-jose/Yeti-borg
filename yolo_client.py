import requests
import cv2
import json

# needs to be changed to the ngrok url or to the local ip address
URL = "http://127.0.0.1:5000/yolo"


def main(**args):
    # make a request to the server
    image = args["image"]
    final_project = args["final_project"]

    request_json = json.dumps({"image": image.tolist()})

    # convert the image to base64 format and send it to the server
    image = cv2.imencode(".jpg", image)[1].tobytes()

    result = requests.post(
        URL, files={"image": image}, 
        data={"final_project": final_project}).json()

    return result
