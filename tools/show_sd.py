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

import busio
import pins
import storage
import sdcardio
import os

def dump_file(name):
  with open(f"/sd/{name}","rt") as file:
    print(file.read())

def del_file(name):
  os.remove(f"/sd/{name}")

spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
sdcard = sdcardio.SDCard(spi,pins.PIN_SD_CS)
vfs    = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

csv = os.listdir("/sd")

print("files on /sd:")
for f in csv:
  print(f"   {f}")

print("\nexample usage:\n")
print("  show_sd.dump_file('message.log')")
print("  show_sd.dump_file('abc.csv')")
print("  show_sd.del_file('abc.csv')\n")
