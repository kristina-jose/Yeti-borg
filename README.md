# Connecting to the pi
- update the wpa_supplicant.conf file with your wifi credentials
- copy the wpa_supplicant.conf file to the boot partition
- insert the SD card into the pi
- connect the pi to the power
- ssh into the pi using the default credentials (pi/raspberry) and hostname (raspberrypi.local)

# Setting up the pi for robot challenges

## setup yolo server on separate machine

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
```bash
python 
```

