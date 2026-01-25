#-----------------------------------------------------------------------------
# Configuration example for a datalogger running on a datalogger PCB.
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- DL identification   ----------------------------------------------------

LOGGER_NAME  = 'DL1 on PCB v2'
LOGGER_ID    = 'DL1'
LOGGER_LOCATION = '@Lab'
LOGGER_TITLE = f'{LOGGER_ID}: {LOGGER_LOCATION}'

# --- active time   ----------------------------------------------------------

STROBE_MODE = True     # power off between measurements
INTERVAL    = 60       # ignored if TIME_TABLE is set

# Example: Mo-Fr from 07:00-17:45 every 15 minutes
TIME_TABLE = [
  ((7,17,1),(0,59,15)),
  ((7,17,1),(0,59,15)),
  ((7,17,1),(0,59,15)),
  ((7,17,1),(0,59,15)),
  ((7,17,1),(0,59,15)),
  None,
  None,
  ]

# --- hardware   -------------------------------------------------------------

HAVE_SD      = True
HAVE_PCB     = True
HAVE_DISPLAY = 'Inky-Pack'

# --- LoRa configuration   ---------------------------------------------------

HAVE_LORA            = True
LORA_FREQ            = 868
LORA_TX_POWER        = 23
LORA_NODE_ADDR       = 1        # this DL-node
LORA_BASE_ADDR       = 0        # address of gateway
LORA_QOS             = 0        # 0: fastest, 7: most reliable

# --- sensors, tasks and csv filename   ---------------------------------------

SENSORS      = "id dcode battery aht20"
CSV_FILENAME = "/sd/DL-{ID}-data.csv"
TASKS        = "save_data send_lora update_display"

# with a connected PC and logging to console, use:
#TASKS        = "dump_data save_data send_lora update_display"
