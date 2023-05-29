import flask
import cv2
import yolo
import numpy as np

# create a Flask app to return the results from yolo

app = flask.Flask(__name__)

def get_color_of_object(img, bbox):
    x, y, w, h = bbox
    roi = img[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv_roi)
    average_color = np.average(hue)
    
    color = "Undefined"
        
    # now we write i for 180 max value of hue
    if average_color>118 and average_color<=149:
        color= "BLUE"
    elif average_color>=0 and average_color<=20 or average_color>=150 and average_color<=180:
        color= "RED"
    elif average_color>=40 and average_color<=118:
        color= "GREEN"
    
    print(average_color, color)
    return color, average_color

@app.route("/yolo", methods=["POST"])
def recognize():
    print("request received")
    # read the image in base64 format
    image = flask.request.files["image"].read()
    image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    result = yolo.main(image, crop=True)
    
    # save the image
    import os
    files = os.listdir("server")
    files = [int(file.strip(".jpg")) for file in files if file.endswith(".jpg") and file.endswith("_result.jpg") == False]
    
    if len(files) == 0:
        new_file = 0
    else:
        max_file = max(files)
        new_file = max_file + 1
    cv2.imwrite(f"server\\{new_file}.jpg", image)

    # among the boxes keep only cups
    result = [res for res in result if res["label"] == "cup"]

    color = None
    
    # get the color of the cup
    for res in result:
        color, average_color = get_color_of_object(image, res["box"])
        res.update({"color" : color})
        res.update({"average_color" : average_color})
        continue
    
    # if there are two green cups change the higher one to blue
    green_list = [res for res in result if res["color"] == "GREEN"]
    remaining_list = [res for res in result if res["color"] != "GREEN"]
    
    if len(green_list) == 2:
        # sort the green list by average color
        green_list = sorted(green_list, key=lambda x: x["average_color"])
        green_list[1].update({"color" : "BLUE"})
        remaining_list.append(green_list[1])
        remaining_list.append(green_list[0])
        result = remaining_list
    
    print(result)
        
    # draw the bounding boxes on the image and save it
    for res in result:
        x, y, w, h = res["box"]
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(image, f"{res['label']} {res['distance']:.2f}, {res['color']}"
                    , (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imwrite(f"server\\{new_file}_result.jpg", image)
    
    return flask.jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)