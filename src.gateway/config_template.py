#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular. Configuration constants.
#
# Copy this file to config.py and modify according to your needs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# hardware configuration
HAVE_RTC   = None
HAVE_SD    = None
GW_RX_TYPE = 'Lora'
GW_TX_TYPE = 'Blues'        # 'Blues' | 'Noop'

# ----------------------------------------------------------------------------
# LoRa configuration
LORA_FREQ       = 433.0     # frequency 433, 868, 915
LORA_NODE_ADDR  = 0         # gateway node-address
LORA_ACK_DELAY  = 0.1       # delay time before sending ACK
LORA_TX_POWER   = 23        # transmit power (max: 23)

# ----------------------------------------------------------------------------
# action to perform when receiving data
#   None:  no action, just print to log
#   False: buffer data to notecard, sync after active window
#   True:  don't buffer data, sync to Notehub immediately
SYNC_BLUES_ACTION = True

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
# technical constants, don't change unless you know why

RECEIVE_TIMEOUT  = 1.0      # single receive wait-time
GET_TIME_REPEATS = 3        # how many times card.time() is executed
MAX_SYNC_TIME    = 300      # number of seconds to wait for a sync

# ----------------------------------------------------------------------------
# Development-mode (useful only for developers with a connected console)

DEV_MODE   = False
