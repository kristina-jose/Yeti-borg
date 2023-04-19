import cv2
import numpy as np

# Load the Tiny YOLOv3 model
net = cv2.dnn.readNet("./tiny_yolo/yolov2-tiny.weights", "./tiny_yolo/yolov2-tiny.cfg")

# Load the classes file
with open("./tiny_yolo/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# this is the focal length of the camera for pi camera v1 in pixels
FOCAL_LENGTH = 500 # 2714.3  2571.4  # calculated 500

# this is the height of the object in cm
OBJECT_HEIGHT = 7

# distance from camera to object in cm
DISTANCE = 30

def detect_objects(image, result_image=False, calibrate=False):
    """Detect objects in an image using the Tiny YOLOv3 model.	
        Args:
            image: The image to detect objects in. This is a numpy array.
            result_image: Whether to save the image with the bounding boxes drawn on it.
        
        returns: A list of objects detected in the image. Each object is a dictionary with the following keys:
            label: The label of the object.
            box: The bounding box of the object.
            distance: The distance to the object in cm.
    """
    # # Load the image
    # image = cv2.imread("test_image\\2.jpg")
    
    # Create a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)

    # Set the input for the neural network
    net.setInput(blob)

    # Get the output layer names
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # Forward pass the image through the network
    outputs = net.forward(output_layers)

    # Find the detected objects
    conf_threshold = 0.5
    nms_threshold = 0.4
    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > conf_threshold:
                center_x = int(detection[0] * image.shape[1])
                center_y = int(detection[1] * image.shape[0])
                w = int(detection[2] * image.shape[1])
                h = int(detection[3] * image.shape[0])
                x = center_x - w // 2
                y = center_y - h // 2

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to remove overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    detected_objects = []
    
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            
            # Calculate the distance to the object
            distance = (OBJECT_HEIGHT * FOCAL_LENGTH) / h
            
            if calibrate:
                focal_length = (h * DISTANCE) / OBJECT_HEIGHT
                detected_objects.append({"label": label, "box": boxes[i], "distance": distance, "focal_length": focal_length})
            else:
                detected_objects.append({"label": label, "box": boxes[i], "distance": distance})
            
            if result_image:
                color = (255, 0, 0)
                cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
                # cv2.putText(image, f"{label} {confidence:.2f} {distance:.2f}m", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)    
    
    # display the image until any key is pressed
    if result_image:
        cv2.imwrite("yolo_result.jpg", image)

    return detected_objects
