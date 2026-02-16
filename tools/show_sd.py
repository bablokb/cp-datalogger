#-----------------------------------------------------------------------------
# Show contents of SD-card from the REPL.
#
# Run "from tools import show_sd" and then one of the commands printed.
# 
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import atexit
import busio
import pins
import storage
import sdcardio
import os

import config

# --- atexit processing   ----------------------------------------------------

def at_exit(spi):
  """ release spi """
  print(f"releasing {spi}")
  spi.deinit()

# --- helper methods   -------------------------------------------------------

def dump_file(name):
  with open(f"{prefix}/{name}","rt") as file:
    print(file.read())

def del_file(name):
  os.remove(f"{prefix}/{name}")

# --- main program   ---------------------------------------------------------

if getattr(config,"HAVE_SD",False):
  try:
    spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
    sdcard = sdcardio.SDCard(spi,pins.PIN_SD_CS)
    vfs    = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    print("SD-card mounted on /sd")
    atexit.register(at_exit,spi)
    prefix = "/sd"
  except:
    print("no SD-card present")
    while True:
      pass

else:
  # give /saves a try
  try:
    os.listdir("/saves")
    prefix = "/saves"
  except:
    print("no SD-card configured")
    while True:
      pass

csv = os.listdir(prefix)

print(f"files on {prefix}:")
for f in csv:
  print(f"   {f}")

print("\nexample usage:\n")
print("  show_sd.dump_file('message.log')")
print("  show_sd.dump_file('abc.csv')")
print("  show_sd.del_file('abc.csv')\n")
