#-----------------------------------------------------------------------------
# Sensor definition for DS18B20.
#
# Naming convention:
#   - filenames in lowercase (ds18b20.py)
#   - class name the same as filename in uppercase (DS18B20)
#   - the constructor must take five arguments (config,i2c0,ic1,spi0,spi1)
#     and probe for the device
#   - i2c1 is the default i2c-device and should be probed first
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# This sensor is not an I2C-sensor, but uses the 1-wire protocol.
# The code needs the configuration-variable PIN_ONE_WIRE.
#
# The code scans the bus for all DS18B20 and returns the values
# sorted according to the ROM-address.


from log_writer import Logger
g_logger = Logger()

import board
import time
from adafruit_onewire.bus import OneWireBus, OneWireAddress
import adafruit_ds18x20

PIN_ONE_WIRE = board.GP27
 
class DS18B20:
  formats = ["T/18B:", "{0:.1f}°C"]
  headers = 'T/18B °C,'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    ow_bus = OneWireBus(PIN_ONE_WIRE)
    while True:
      g_logger.print("scanning for ds18b20")
      addresses = [d for d in ow_bus.scan() if d.family_code == 0x28 ]
      if len(addresses):
        break
      else:
        time.sleep(0.05)
    addresses.sort(key=lambda a: a.rom)
    self.ds18b20 = []
    for address in addresses:
      sn = "-".join(hex(b) for b in address.serial_number)
      g_logger.print(f"found {sn}")
      self.ds18b20.append(
        (adafruit_ds18x20.DS18X20(ow_bus,address),address.rom)
      )
    DS18B20.formats = len(addresses)*DS18B20.formats
    DS18B20.headers = (len(addresses)*DS18B20.headers)[:-1]
    
  def read(self,data,values):
    """ read sensor """
    data["ds18b20"] = {}
    record = ""
    sep    = ""
    for ds18b20,rom in self.ds18b20:
      t = ds18b20.temperature
      data["ds18b20"]["-".join(hex(b) for b in rom)] = t
      values.extend([None,t])
      record += f"{sep}{t:0.1f}"
      sep = ","
    return record
