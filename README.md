# flask-mbient-backend
A simple Flask server backend for interfacing with Mbient on a Raspberry Pi

### Operating Systems
- Raspbian

### Known System Dependencies
- Python 3.5
- libbluetooth-dev
- libboost-dev-all
- mosquitto

### Python Dependencies
- metawear
- paho-mqtt
- Flask

### How to run:
- Start the MQTT broker, Mosquitto, in the background:
  
  ```mosquitto -c mosquitto.conf```
- Set the environment variables for Flask
  
  ```export FLASK_APP=server.py```
- Run the Flask web app

  ```flask run --hostname=0.0.0.0 --port=5000```
  
- From here, you can access the web app on `localhost:5000` on your browser. You can then either:
  - Start the Mbient device: `localhost:5000/start/<device MAC address>`
  - Stop the Mbient device: `localhost:5000/stop`
 
- You can also tune in to the MQTT data channel using the topic `DATA` at `localhost:8080` through any MQTT client
  
