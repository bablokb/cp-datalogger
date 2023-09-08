#-----------------------------------------------------------------------------
# Sample LoRa code for a gateway on a Pi (-Zero)
#
# Adapted from:
#
#   Adafruit IO LoRa Gateway
#   Learn Guide: https://learn.adafruit.com/multi-device-lora-temperature-network
#   by Brent Rubell for Adafruit Industries
#   SPDX-FileCopyrightText: 2019 Brent Rubell for Adafruit Industries
#   SPDX-License-Identifier: MIT
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import busio
import board
from digitalio import DigitalInOut, Direction, Pull

import adafruit_ssd1306
import adafruit_rfm9x

# --- constants   -------------------------------------------------------------

INTERVAL = 2
RADIO_FREQ_MHZ  = 868.0
LORA_STATION_ID = 0
HEADER_TEXT = 'Datalogger Gateway'
WAIT_TEXT   = 'listening...'
ERROR_TEXT  = 'invalid data'

# --- buttons (unused)   ------------------------------------------------------
# Button A
#btnA = DigitalInOut(board.D5)
#btnA.direction = Direction.INPUT
#btnA.pull = Pull.UP

# Button B
#btnB = DigitalInOut(board.D6)
#btnB.direction = Direction.INPUT
#btnB.pull = Pull.UP

# Button C
#btnC = DigitalInOut(board.D12)
#btnC.direction = Direction.INPUT
#btnC.pull = Pull.UP

# --- display   --------------------------------------------------------------

i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
display.fill(0)
display.show()
width  = display.width
height = display.height

# --- LoRa   -----------------------------------------------------------------

CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.node = LORA_STATION_ID

# --- update display   -------------------------------------------------------

def update_display(lines=[]):
  """ update display """
  display.fill(0)
  display.text(HEADER_TEXT, 0, 0, 1)
  offset = 8
  for line in lines:
    display.text(line,0,offset,1)
    offset += 8
  display.show()

# --- process data   ---------------------------------------------------------

def process_data(data):
  """ process data (e.g. send into the cloud) """
  print(f"data: {data}")

# --- main-loop   ------------------------------------------------------------

update_display([WAIT_TEXT])
while True:
  packet = None

  # check for packet rx
  packet = rfm9x.receive(with_ack=True)
  if packet is None:
    continue

  # Decode packet: assume it is csv with a timestamp as first field
  try:
    data = packet.decode(encoding="UTF-8")
    process_data(data)
    values = data.split(',')         # expect csv
    ts = values[0].split('T')[1]     # removes date from timestamp
    # Display packet information
    update_display([ts,values[1],values[2]])
  except:
    update_display([ERROR_TEXT])
  time.sleep(INTERVAL)
