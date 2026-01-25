#-----------------------------------------------------------------------------
# Configuration example for a gateway running on datalogger hardware.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- GW identification   ----------------------------------------------------

GW_NAME     = 'GW'
GW_ID       = 'GW'
GW_LOCATION = '@Lab'
GW_TITLE    = '{GW_ID}: {GW_LOCATION}'

# --- hardware   -------------------------------------------------------------

HAVE_SD      = True
HAVE_DISPLAY = None
HAVE_RTC     = "PCF8523(1)"
HAVE_PM      = True
#HAVE_OLED   = "1,0x3c,128,32"

# --- LoRa configuration   ---------------------------------------------------

LORA_FREQ       = 868       # frequency 433, 868, 915
LORA_NODE_ADDR  = 0         # this is the gateway node-address
LORA_TX_POWER   = 23        # transmit power (max: 23)
LORA_QOS        = 0         # 0: fastest, library default; 3: default

# --- receiver and transmitter   ---------------------------------------------

GW_RX_TYPE = 'Lora'
GW_TX_TYPE = 'Noop'        # no upstream

# --- tasks (what to do with received data)   --------------------------------

TASKS = "save_data"        # only save data to SD
B_TASKS = "bc_save_data"   # also save broadcast data to SD

# create an output file for every datalogger
CSV_FILENAME = "/sd/{GW_ID}_data_{ID}.csv"

# --- active time   ----------------------------------------------------------

# always on ...
ON_DURATION = 0

# ... or time-table base

# start every hour, active 55 minutes
# TIME_TABLE = [
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60)),
#   ((0,24,1),(0,59,60))
#   ]
# ON_DURATION = 55



