#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import busio
import board
import busio
from digitalio import DigitalInOut, Direction, Pull

# --- imports for display
import displayio
from terminalio import FONT
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306

# --- imports for LoRa
import adafruit_rfm9x

# --- imports for Notecard
import notecard
from notecard import hub, card, note, file

# --- constants   -------------------------------------------------------------

SYNC_BLUES = None         # None, True, False
INTERVAL = 0.1
RADIO_FREQ_MHZ  = 868.0
LORA_STATION_ID = 0
HEADER_TEXT = 'Datalogger Gateway'
WAIT_TEXT   = 'listening...'
ERROR_TEXT  = 'invalid data'

# pin defs for (generic) Feather
#PIN_SDA  = board.SDA
#PIN_SCL  = board.SCL
#PIN_SCK  = board.SCK
#PIN_MISO = board.MISO
#PIN_MOSI = board.MOSI
#PIN_CS   = board.A5
#PIN_RST  = board.A4

# pin defs for RP2040-Challenger-LoRa
PIN_SDA  = board.SDA
PIN_SCL  = board.SCL
PIN_SCK  = board.RFM95W_SCK
PIN_MISO = board.RFM95W_SDI
PIN_MOSI = board.RFM95W_SDO
PIN_CS   = board.RFM95W_CS
PIN_RST  = board.RFM95W_RST

# --- display   --------------------------------------------------------------

displayio.release_displays()
i2c = busio.I2C(sda=PIN_SDA,scl=PIN_SCL)
display_bus = displayio.I2CDisplay(i2c,device_address=0x3c)
display = SSD1306(display_bus,width=128,height=32)

group = displayio.Group()
lbl = label.Label(FONT,text=HEADER_TEXT,color=0xFFFFFF,line_spacing=1.05,
                    anchor_point=(0,0),x=0,y=4
                    )
group.append(lbl)
display.show(group)

# --- LoRa   -----------------------------------------------------------------

cs  = DigitalInOut(PIN_CS)
rst = DigitalInOut(PIN_RST)
spi = busio.SPI(PIN_SCK, MOSI=PIN_MOSI, MISO=PIN_MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, rst, RADIO_FREQ_MHZ)
rfm9x.node = LORA_STATION_ID
rfm9x.ack_delay = 0.1
rfm9x.tx_power = 23

# --- Notecard   -------------------------------------------------------------

my_card = notecard.OpenI2C(i2c,0,0,debug=False)
hub.set(my_card,mode="minimum")

# --- update display   -------------------------------------------------------

def update_display(lines=[]):
  """ update display """

  txt = f"{HEADER_TEXT}\n{lines[0]}"
  if len(lines) > 1:
    txt = f"{txt}\n{lines[1]}: {lines[2]}"
  lbl.text = txt

# --- process data   ---------------------------------------------------------

def process_data(data,id):
  """ process data (currently just queue to notecard) """
  start = time.monotonic()
  print(f"data: {data}")
  if SYNC_BLUES is not None:
    resp = note.add(my_card,
                    file=f"dl_{id}.qo",
                    body={"data":data},
                    sync=SYNC_BLUES)
  else:
    resp = "action: noop"
  print(f"{time.monotonic()-start}: action: {SYNC_BLUES}, {resp=}")

# --- main-loop   ------------------------------------------------------------

update_display([WAIT_TEXT])
while True:
  packet = None

  # check for packet rx. Default timeout is 0.5
  packet = rfm9x.receive(with_ack=True,timeout=1.0)
  if packet is None:
    continue
  snr  = rfm9x.last_snr
  rssi = rfm9x.last_rssi

  # Decode packet: assume it is csv with a timestamp as first field
  try:
    data = packet.decode()
    values = data.split(',')         # expect csv
    process_data(data,values[1])     # expect id as second field
    ts = values[0].split('T')[1]     # removes date from timestamp
    # Display packet information
    update_display([f"{ts} ({snr}/{rssi})",values[1],values[2]])
  except:
    update_display([ERROR_TEXT])
  time.sleep(INTERVAL)
