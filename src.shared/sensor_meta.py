#-----------------------------------------------------------------------------
# Sensor metadata.
#
# Data definition and tools for processing csv data collected by the
# datalogger.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- mapping of sensor to DCODE (see src/sensors/dcode.py)   ----------------

SENSOR_MAP = {
  "id":      "0",
  "dcode":   "1",
  "battery": "2",
  "aht20":   "3",
  "am2320":  "4",
  "bh1750":  "5",
  "bme280":  "6",
  "bmp280":  "7",
  "ds18b20": "8",
  "ens160":  "9",
  "htu31d":  "A",
  "ltr559":  "B",
  "mcp9808": "C",
  "pdm":     "D",
  "pms5003": "E",
  "scd40":   "F",
  "scd41":   "G",
  "sht45":   "H",
  "meteo":   "I",
  "location": "J",
  "cputemp": "K",
  "mhz19":   "L",
  "hdc302x": "M",
  "sen6x":   "N",
  "lm66200": "O",
  "tm_power": "P",
  }

# --- mapping of DCODE to sensor properties: dcode -> (sensor,fields)   ------

# A (single) sensor with a variable field count must be last in the
# SENSORS definition

DCODE_MAP = {
  "0": ("id",1),
  "1": ("dcode",1),
  "2": ("battery",1),
  "3": ("aht20",2),
  "4": ("am2320",2),
  "5": ("bh1750",1),
  "6": ("bme280",4),
  "7": ("bmp280",3),
  "8": ("ds18b20",1),    # variable, 1-n
  "9": ("ens160",4),     # has more fields in test-mode
  "A": ("htu31d",2),
  "B": ("ltr559",1),
  "C": ("mcp9808",1),
  "D": ("pdm",1),
  "E": ("pms5003",9),
  "F": ("scd40",3),      # has more fields in test-mode
  "G": ("scd41",3),      # has more fields in test-mode
  "H": ("sht45",2),
  "I": ("meteo",7),
  "J": ("location",1),
  "K": ("cputemp",1),
  "L": ("mhz19",2),
  "M": ("hdc302x",2),
  "N": ("sen6x",13),
  "O": ("lm66200",1),
  "P": ("tm_power",3),    # variable, 3-n*3
  }

# --- split csv record according to dcode   ----------------------------------

def split_csv(record, dcode_index=2):
  """ split record according to dcode """

  fields = record.split(',')
  ts = fields[0]
  result = []
  index = 1
  id = None
  for dc in fields[dcode_index]:
    item = {}
    item["sensor"] = DCODE_MAP[dc][0]
    if dc == fields[dcode_index][-1]:
      # last sensor, consume all remaining fields
      item["data"] = fields[index:]
    else:
      # consume fields according to metadata
      item["data"] = fields[index:index+DCODE_MAP[dc][1]]

    # extract id, ignore id and dcode
    if item["sensor"] == 'id':
      id = item["data"][0]
    elif item["sensor"] == 'dcode':
      pass
    else:
      result.append(item)
    index += DCODE_MAP[dc][1]

  return {"ts": ts,"id": id, "record:": result}
