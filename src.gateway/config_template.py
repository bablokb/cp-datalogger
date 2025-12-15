#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular. Configuration constants.
#
# Copy this file to config.py and modify according to your needs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- GW identification   ------------------------------------------------

GW_NAME     = 'My Gateway'
GW_ID       = 'xxx'            # any string (without commas)
GW_LOCATION = 'yyy'            # use e.g. Plus Code (no commas)
GW_TITLE    = 'zzz'            # used for the display

# ----------------------------------------------------------------------------
# hardware configuration
HAVE_RTC   = None
HAVE_SD    = None
GW_RX_TYPE = 'Lora'
GW_TX_TYPE = 'Noop'        # 'Blues' | 'Noop' | 'UDP'

# ----------------------------------------------------------------------------
# LoRa configuration
LORA_FREQ       = 433.0           # frequency 433, 868, 915
LORA_NODE_ADDR  = 0               # gateway node-address
LORA_ACK_DELAY  = 0.1             # delay time before sending ACK
LORA_TX_POWER   = 23              # transmit power (max: 23)
LORA_GW_RECEIVE_TIMEOUT  = 1.0    # single receive wait-time

# ----------------------------------------------------------------------------
# gw_tx_blues specific configuration
#
# action to perform when receiving data
#   None:  no action, just print to log
#   False: buffer data to notecard, sync after active window
#   True:  don't buffer data, sync to Notehub immediately
BLUES_SYNC_ACTION = True
BLUES_GET_TIME_RETRIES = 3        # how many times card.time() is executed
BLUES_MAX_SYNC_TIME    = 300      # number of seconds to wait for a sync

# ----------------------------------------------------------------------------
# gw_tx_udp specific configuration
#
#UDP_HOST =
#UDP_PORT =

# --- tasks to execute after receiving data  - -------------------------------
# See the docs for a complete list of tasks and for special task configuration.

TASKS = "save_data update_oled tx_send"

#CSV_FILENAME = "/sd/data_{GW_ID}_{ID}.csv"    # GW_ID and LOGGER_ID in name
#CSV_FIELDNR_ID = 1                            # 0-based fieldnr for LOGGER_ID

# ----------------------------------------------------------------------------
# uptime configuration. The template values configure a single active window
# (from hours 7 to 7 at minutes 0 to 0 every day). On duration is 10 hours.
#
# To reduce the power consumption, the time-table and on-duration can be
# fine tuned to match the uptime of the dataloggers.
TIME_TABLE = [
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1)),
  ((7,7,1),(0,0,1))
  ]
ON_DURATION = 600   # 600 = 10*60

# ----------------------------------------------------------------------------
# Development-mode (useful only for developers with a connected console)

DEV_MODE   = False
