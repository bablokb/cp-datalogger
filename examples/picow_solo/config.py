#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# An example for the Pico-W without any additional components.
# It will query Open-Meteo and print the results to the console.
#
# You should adapt the latitude/longitude settings to your location.
# Also keep in mind that Open-Meteo updates their data every 15
# minutes, so it is not necessary to poll more often.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- Logger identification   ------------------------------------------------

LOGGER_NAME     = 'Open-Meteo'
LOGGER_ID       = 'OM1'            # any string (without commas)
LOGGER_LOCATION = '@Home'          # use e.g. Plus Code (no commas)

SENSORS = "meteo"

#METEO_LATITUDE  = 
#METEO_LONGITUDE = 

TASKS = "dump_data"
SHOW_UNITS = False         # write as CSV-data to serial console

STROBE_MODE = False     # use continuous mode
INTERVAL    = 60        # ignored, but forces light-sleep (int<61)

# sample at 01, 16, 31, 46
TIME_TABLE = [
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15)),
  ((7,18,1),(1,59,15))
  ]

HAVE_PM  = False
HAVE_RTC = None
HAVE_SD  = False
