#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# Example using a Pimoroni Badger2040W (without SD-card).
# This configuration assumes that a SCD41 is attached to the Stemma/Qt
# connector of the Badger2040W.
#
# Note that the power-management of the Badger2040W is only active on
# battery-power.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

NET_UPDATE  = True        # update RTC from time-server if time is invalid

STROBE_MODE = True
INTERVAL    = 60          # ignored, because of TIME_TABLE below!

# sample once every five minutes from 08:00 to 19:55
TIME_TABLE = [
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5)),
  ((8,19,1),(0,59,5))
  ]

HAVE_SD       = False
HAVE_DISPLAY  = "internal"
HAVE_RTC      = "PCF85063(0)"
HAVE_I2C0     = True
HAVE_PM       = True
SHUTDOWN_HIGH = False

SENSORS      = "id battery scd41"

LOGGER_NAME  = 'badger2040w'
LOGGER_ID    = '2040W_1'
LOGGER_LOCATION = '@Home'
LOGGER_TITLE    = "CO2/T/Hum @ Home"

# tasks to execute after data-collection
TASKS = "update_display"
