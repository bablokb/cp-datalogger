#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# !!! This file is not maintained within Github !!!
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

TEST_MODE   = True        # set to FALSE for a production setup
BLINK_TIME_START  = 0.5   # blink time of LED before start of data-collection
BLINK_TIME_END  = 0.25    # blink time of LED  after finish of data-collection
BLINK_START = 3           # blink n times before start of data-collection
BLINK_END   = 5           # blink n times after finish of data-collection

NET_UPDATE  = True        # update RTC from time-server if time is invalid

# tasks to execute after data-collection
TASKS = "dump_data save_data update_display"

# time table: one entry per day (starting with Monday)
#             ((h_start,h_end,h_inc),(m_start,m_end,m_inc))
# The example has Mo-Fr from 07:00-17:45 every 15 minutes
#TIME_TABLE = [
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  (None,None),
#  (None,None)
#  ]

STROBE_MODE = True      # strobe-mode or continuous-mode
INTERVAL    = 60        # interval (in seconds)

# hardware setup
HAVE_I2C0    = False               # also use second I2C-bus
HAVE_PCB     = True                # The Pico is running on the pcb described here: https://github.com/pcb-pico-datalogger
HAVE_SD      = False               # The PCB has an sd card inserted (or an sd card is connected otherwise)
CSV_FILENAME = "/sd/log_{ID}_{YMD}.csv"
HAVE_DISPLAY = 'Inky-Pack'         # 'Inky-Pack', 'Display-Pack' or None
HAVE_LIPO = False                  # True, False

# List of sensors. Each needs a <sensor>.py file.
# An entry must be any off (no spaces allowed!):
#   sensor
#   sensor(bus)          bus = 0|1
#   sensor(addr)         addr = 0xZZ
#   sensor(addr,bus)
#
# When no bus is provided, busses are probed in the order i2c1,i2c0.
# When no address is provided, the default address as configured in
# the driver is used.
SENSORS = "id battery"

SHOW_UNITS = False # Show units in the csv output
SIMPLE_UI  = False # use simple UI

# Logger identification constants
LOGGER_NAME  = 'Darasa Kamili'  # Perfect Classroom
LOGGER_ID    = '000'            # Change this to your logger id
LOGGER_LOCATION = '6G5X46G4+XQ' # Plus Code for Dar airport
LOGGER_TITLE = LOGGER_NAME + " " + LOGGER_LOCATION

# font for the display
FONT_DISPLAY     = 'DejaVuSansMono-Bold-18-subset'

# LoRa configuration
LORA_ENABLE_TIME = 0
LORA_ACK_WAIT    = 0.5
LORA_ACK_RETRIES = 3
LORA_FREQ        = 433.0
LORA_TX_POWER    = 13     # default: 13, range: 5-23
LORA_NODE_ADDR   =
LORA_BASE_ADDR   =

# UDP (WLAN) configuration
UDP_IP = '1.2.3.4'
UDP_PORT = 6600
