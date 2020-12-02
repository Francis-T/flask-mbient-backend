import time
import json

from enum import Enum

from mbientlab.metawear import MetaWear, parse_value
from mbientlab.metawear import libmetawear as lmw
from mbientlab.metawear.cbindings import *

import paho.mqtt.publish as mqtt_publish

class MbientBackend():
  def __init__(self, device_addr, log_flags=["ERROR", "WARNING"]):
    self.device = MetaWear(device_addr)
    self.samples = 0
    self.callback_acc = FnVoid_VoidP_DataP(self.handle_accel_data)
    self.callback_gyr = FnVoid_VoidP_DataP(self.handle_gyro_data)
    self.log_flags = log_flags

    self.target_servers = {}

    # Attempt to connect
    self.log("INFO", "Connecting to device...")
    self.device.connect()
    self.log("INFO", "Connected.")

    return

  def register_mqtt_server(self, addr, port, label=None):
    if label == None:
      label = str(addr) + ":" + str(port)

    # Add it to the target servers list
    self.target_servers[label] = {
      'label' : label,
      'address' : addr,
      'port' : port,
    }

    return

  def unregister_mqtt_server(self, label):
    # Remove it from the target servers list
    if label in self.target_servers.keys():
      del self.target_servers[label]

    return

  def handle_accel_data(self, ctx, data):
    return self.handle_data(ctx, data, "ACCEL")

  def handle_gyro_data(self, ctx, data):
    return self.handle_data(ctx, data, "GYRO")

  def handle_data(self, ctx, data, data_type):
    self.log("DEBUG", "%s -> %s" % (self.device.address, parse_value(data)))
    parsed_data = parse_value(data)
    data_dict = {
      'ts' : time.time(), # Note we can get this from the data contents itself
      'type' : data_type,
      'contents' : {
        'x' : parsed_data.x, 'y' : parsed_data.y, 'z' : parsed_data.z,
      }
    }

    data_str = json.dumps(data_dict)

    topics = "DATA"

    for srv_id in self.target_servers.keys():
      target = self.target_servers[srv_id]
      mqtt_publish.single(topics, payload=data_str,
                                  hostname=target['address'],
                                  port=target['port'])
    return

  def start(self):
    if self.device == None:
      self.log("ERROR", "Device not available")
      return False

    dev_board = self.device.board

    self.log("INFO", "Configuring device")
    lmw.mbl_mw_settings_set_connection_parameters(dev_board, 7.5, 7.5, 0, 6000)
    time.sleep(1.5)

    # Subscribe to accelerometer data
    acc = lmw.mbl_mw_acc_get_acceleration_data_signal(dev_board)
    lmw.mbl_mw_datasignal_subscribe(acc, None, self.callback_acc)

    # Subscribe to gyro data
    gyro = lmw.mbl_mw_gyro_bmi160_get_rotation_data_signal(dev_board)
    lmw.mbl_mw_datasignal_subscribe(gyro, None, self.callback_gyr)

    self.log("INFO", "Starting device...")
    # Enable accelerometer sampling
    lmw.mbl_mw_acc_enable_acceleration_sampling(dev_board)
    lmw.mbl_mw_acc_start(dev_board)

    # Enable gyrp sampling
    lmw.mbl_mw_gyro_bmi160_enable_rotation_sampling(dev_board)
    lmw.mbl_mw_gyro_bmi160_start(dev_board)

    self.log("INFO", "Device started.")

    return True

  def stop(self):
    if self.device == None:
      self.log("ERROR", "Device not available")
      return False

    dev_board = self.device.board

    self.log("INFO", "Stopping device...")
    lmw.mbl_mw_acc_stop(dev_board)
    lmw.mbl_mw_acc_disable_acceleration_sampling(dev_board)

    lmw.mbl_mw_gyro_bmi160_stop(dev_board)
    lmw.mbl_mw_gyro_bmi160_disable_rotation_sampling(dev_board)

    # Unsubscribe from accelerometer data
    acc = lmw.mbl_mw_acc_get_acceleration_data_signal(dev_board)
    lmw.mbl_mw_datasignal_unsubscribe(acc)

    # Unsubscribe from gyro data
    gyro = lmw.mbl_mw_gyro_bmi160_get_rotation_data_signal(dev_board)
    lmw.mbl_mw_datasignal_unsubscribe(gyro)
    self.log("INFO", "Device stopped.")

    return True

  def cleanup(self):
    if self.device == None:
      self.log("ERROR", "Device not available")
      return False

    # Attempt to connect
    self.log("INFO", "Disconnecting from device...")
    lmw.mbl_mw_debug_disconnect(self.device.board)
    self.log("INFO", "Disconnected.")

    return True

  def log(self, log_level, message):
    if log_level in self.log_flags:
      print("[MbientBackend][{}] {}".format(log_level, message))
    # print(f"[MbientBackend] {message}")
    return


if __name__ == "__main__":
  mb = MbientBackend("FF:D8:D9:B5:2E:E2")
  mb.register_mqtt_server("127.0.0.1", 10001)

  try:
    mb.start()
    time.sleep(5.0)

  finally:
    mb.stop()
    mb.unregister_mqtt_server("127.0.0.1:10001")
    mb.cleanup()


