#-----------------------------------------------------------------------------
# Start broadcast-mode: run LoRa communication to optimize antenna setup
#
# Broadcast-data is in CSV-format:
#     B,<ts>,<id>,<nr>,<node>
# with a fixed "B", followed by the timestamp, logger-id, packet-number
# and LoRa-node-id.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
from digitalio import DigitalInOut, Pull, Direction

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')
g_logger.print("!!! Starting in Broadcast-Mode !!!")

from broadcast_impl import Broadcast
from settings import Settings
g_config = Settings(g_logger)
g_config.import_config()

import pins

from sleep import TimeSleep

# --- main program start   ---------------------------------------------------

if hasattr(pins,"PIN_SWD"):
  switch_d = DigitalInOut(pins.PIN_SWD)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True
elif hasattr(pins,'PIN_LED'):
  switch_d = DigitalInOut(pins.PIN_LED)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True

app = Broadcast()
app.update_time()
TimeSleep.light_sleep(duration=5)

app.clear()
app.update_info([f"Node: {g_config.LORA_NODE_ADDR}, ID: {g_config.LOGGER_ID}"])

start = time.monotonic()
while True:
  stime = max(0,app.interval - (time.monotonic()-start))
  g_logger.print(f"Broadcast: next cycle in  {stime}s...")
  TimeSleep.light_sleep(duration=stime)
  app.send_packet()
  app.update_display()
  start = time.monotonic()
