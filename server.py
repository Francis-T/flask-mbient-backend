from flask import Flask
from backend import MbientBackend

mbientBackend = None
app = Flask(__name__)

@app.route('/')
def root():
  return "Available commands: start/, stop/, cleanup/"

@app.route('/start/<raw_addr>')
def start(raw_addr):
  global mbientBackend
  device_addr = format_addr(raw_addr)

  #mbientBackend = get_backend(device_addr)
  try:
    if mbientBackend == None:
      mbientBackend = MbientBackend(device_addr)

    mbientBackend.register_mqtt_server("127.0.0.1", 10001)
    mbientBackend.start()
  except Exception as e:
    return "Error Ocurred: " + str(e) + "\n\nPlease try again."

  return "Device started"

@app.route('/stop')
def stop():
  global mbientBackend
  if mbientBackend == None:
    return "Device unavailable"

  mbientBackend.stop()
  mbientBackend.unregister_mqtt_server("127.0.0.1:10001")
  mbientBackend.cleanup()

  mbientBackend = None

  return "Device stopped"

def format_addr(base_addr):
  if len(base_addr) != 12:
    return "Error: Invalid device address (wrong address length)"

  return base_addr[0:2] + ":" + \
         base_addr[2:4] + ":" + \
         base_addr[4:6] + ":" + \
         base_addr[6:8] + ":" + \
         base_addr[8:10] + ":" + \
         base_addr[10:12]


