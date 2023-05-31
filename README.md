# Connecting to the pi
- update the wpa_supplicant.conf file with your wifi credentials
- copy the wpa_supplicant.conf file to the boot partition
- insert the SD card into the pi
- connect the pi to the power
- ssh into the pi using the default credentials (pi/raspberry) and hostname (raspberrypi.local)

# Setting up the pi for robot challenges

## setup yolo server on separate machine

python version 3.9.1 or higher is required for all the dependencies to work

Optional: seup virtual environment
```bash
python -m venv venv

# for windows
venv\Scripts\activate.bat

# for linux
source venv/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Download the yolo weights from https://pjreddie.com/media/files/yolov3.weights and place them in the tiny_yolo folder

Run the server
```bash
python yolo_server.py
```

## Optional: accessing the server over the internet
For accessing the server over the internet install ngrok via https://ngrok.com/download

```bash
# for windows
ngrok.exe http 5000

# for linux
./ngrok http 5000
```

## Yolo client seup for the pi

Install dependencies
```bash
pip install -r requirements.txt
```

Before runnning the client update the ip address in the yolo_client.py file to the ip address of the yolo server
Run the client
```bash
python yolo_client.py
```

# Run Mobile Robot challenge:
Run the following command in order to start the project:
```bash
python mobile_robot.py
```
There will asked to press a number as input:
- Press "0" to start calibrating
- Press "1" to start challenge 1
- Press "2" to start challenge 2
- Press "3" to start challenge 3
- Any other number or letter will lead to exit

The calibrating part consists out of 2 questions:
Enter the angle the robot should make?
Enter the angle the robot did make?
The difference between these answers will lead to an automatically change in the spin, so when you try to calibrate it again, you should be close to the first number you entered. 

# Running Final project:
Run the following command in order to start the project:
```bash
python final_project.py
```
There will asked to press a number as input:
- Press "0" to start calibrating angle
- Press "1" to start calibrating meters
- Press "2" to start final project
