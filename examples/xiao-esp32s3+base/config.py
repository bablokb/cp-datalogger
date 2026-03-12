#-----------------------------------------------------------------------------
# Dev/Test Configuration constants for Datalogger XIAO ESP32S3 + XIAO-Base
#
# Website: https://github.com/cp-datalogger
#-----------------------------------------------------------------------------

# identification
LOGGER_NAME  = 'XIAO ESP32S3'
LOGGER_ID    = 'xiao1'
LOGGER_LOCATION = '@Lab'
LOGGER_TITLE = f'{LOGGER_ID}: {LOGGER_LOCATION}'

# test mode
TEST_MODE   = True
NET_UPDATE  = True
#BLINK_TIME_START  = 0
#BLINK_TIME_END  = 0
#BLINK_START = 0
#BLINK_END   = 0

# sample intervals
STROBE_MODE = False
INTERVAL    = 5
TT_INT     = 1
TT_START   = 1
# TIME_TABLE = [
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT)),
#   ((0,24,1),(TT_START,59,TT_INT))
#   ]

# hardware and display
HAVE_SD      = True
HAVE_PCB     = False
HAVE_I2C0    = False
HAVE_RTC     = "PCF8563(1)"
HAVE_LORA    = False
HAVE_DISPLAY = None

SHOW_UNITS = True

HAVE_OLED    = "1,0x3c,128,64"
OLED_VALUES  = "tm_power(P/tm:) tm_power(V/tm:)"

# sensors and csv filename
SENSORS      = "id dcode tm_power"
CSV_FILENAME = f"/sd/DL-{{ID}}-{SENSORS.replace(' ','_')}.csv"
CSV_HEADER_EXTENDED = True
TM_POWER_HOSTS = ["splug_1"]
TM_POWER_PROPERTIES="P V"        # show only power

# tasks to execute after data-collection
TASKS = "dump_data save_data update_oled"
