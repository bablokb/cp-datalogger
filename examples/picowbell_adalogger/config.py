#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# Using PiCowbell-Adalogger and no display.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

STROBE_MODE = False
INTERVAL    = 10

HAVE_SD       = False
HAVE_DISPLAY  = None
HAVE_RTC      = "PCF8523(0)"
HAVE_I2C0     = True
HAVE_PM       = False
SHUTDOWN_HIGH = True          # in case TPL5110/TPL5111 is used

HAVE_OLED = "0,0x3c,128,64"
OLED_VALUES = "pms5003(PM0.3:) pms5003(PM1.0:)"

SENSORS       = "id battery pms5003"
CSV_FILENAME = f"/sd/particle-data.csv"

LOGGER_NAME  = 'adalogger'
LOGGER_ID    = 'ADA_1'
LOGGER_LOCATION = '@Home'
LOGGER_TITLE = f'{LOGGER_ID}: {LOGGER_NAME}'

# tasks to execute after data-collection
TASKS = "dump_data save_data update_oled"
SHOW_UNITS = True
