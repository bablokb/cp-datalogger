#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# Example using a PiCowbell-Adalogger without display.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

NET_UPDATE  = True        # update RTC from time-server if time is invalid

STROBE_MODE = True
INTERVAL    = 60

HAVE_SD       = True
HAVE_DISPLAY  = None
HAVE_RTC      = "PCF8523(0)"
HAVE_I2C0     = True
HAVE_PM       = True
SHUTDOWN_HIGH = True          # use TPL5110/TPL5111

SENSORS      = "id battery cputemp"
CSV_FILENAME = f"/sd/data-{{ID}}-{SENSORS.replace(' ','_')}.csv"

LOGGER_NAME  = 'adalogger'
LOGGER_ID    = 'ADA_1'
LOGGER_LOCATION = '@Home'

# tasks to execute after data-collection
TASKS = "dump_data save_data"
SHOW_UNITS = True
