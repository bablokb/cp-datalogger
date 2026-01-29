#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# This template file contains common constants that are used in the firmware.
# For a complete list, read the documentation.
#
# Copy this file to config.py and adapt to your needs. config.py itself is
# not maintained in the repo (part of .gitignore).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

# !!! NOTE: everything without comments is mandatory !!!

# --- Logger identification   ------------------------------------------------

LOGGER_NAME     = 'My Datalogger'
LOGGER_ID       = 'xxx'            # any string (without commas)
LOGGER_LOCATION = 'yyy'            # use e.g. Plus Code (no commas)
LOGGER_TITLE    = 'zzz'            # used for the display

# --- destination filename for data (see docs for format)   ------------------

#CSV_FILENAME = "/sd/log_{ID}_{YMD}.csv"

# --- List of sensors (see docs for available sensors)   ---------------------

# An entry must be any of (no spaces allowed!):
#   sensor
#   sensor(bus)          bus = 0|1
#   sensor(addr)         addr = 0xZZ
#   sensor(addr,bus)
#
# When no bus is provided, busses are probed in the order i2c1,i2c0.
# When no address is provided, the default address as configured in
# the driver is used.
#
# Since the display can only show 6 values, you can exclude sensors
# from the display. The data is still recorded in the CSV.
# Entries in 'SENSORS_CSV_ONLY' must match exactly to entries in 'SENSORS'.

SENSORS = "id battery cputemp"
#SENSORS_CSV_ONLY = ""

# --- tasks to execute after data-collection   -------------------------------
# See the docs for a complete list of tasks and for special task configuration.

TASKS = "save_data update_display"

# --- time update   ----------------------------------------------------------

#NET_UPDATE  = True        # update RTC from time-server if time is invalid
#SAVE_WAKEUP = False       # save wakup-time on SD (workaround for buggy batteries)

# --- sample mode and intervals/time-table   ---------------------------------

#STROBE_MODE = True      # strobe-mode or continuous-mode
#INTERVAL    = 900       # interval (in seconds), default: 15 minutes
#TIME_TABLE  = None      # defaults to no time-table

# time table: one entry per day (starting with Monday), ranges are inclusive
#             ((h_start,h_end,h_inc),(m_start,m_end,m_inc))
# Example: Mo-Fr from 07:00-18:45 every 15 minutes
#TIME_TABLE = [
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  ((7,18,1),(0,59,15)),
#  (None,None),
#  (None,None)
#  ]

# --- hardware setup   -------------------------------------------------------

#HAVE_PM      = True          # power-management (e.g. special PCB) available
#SHUTDOWN_HIGH = True
#HAVE_RTC     = "PCF8523(1)"  # RTC on i2c-bus 1
#HAVE_SD      = True          # SD-card support
#HAVE_I2C0    = False         # use second I2C-bus (no more UART!)
#HAVE_LIPO    = False         # True, False
#HAVE_DISPLAY = None          # 'Inky-Pack', 'Display-Pack' or None
#HAVE_LORA    = False         # True, False
#HAVE_OLED    = None          # (bus,addr,width,height), e.g. "0,0x3c,128,64"

# --- LoRa configuration (in case LoRa is available)   -----------------------

LORA_FREQ             = 433.0
LORA_BASE_ADDR        = 0
LORA_NODE_ADDR        = 1
#LORA_QOS             = 2      # default: 2, range: 0-7
#LORA_TX_POWER        = 13     # default: 13, range: 5-23
#LORA_RECEIVE_TIMEOUT = 5.0
