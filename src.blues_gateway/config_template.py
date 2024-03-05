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

# action to perform when receiving data
#   None:  no action, just print to log
#   False: buffer data to notecard, sync after active window
#   True:  don't buffer data, sync to Notehub immediately
SYNC_BLUES_ACTION = True

LORA_FREQ       = 433.0     # frequency 433, 868, 915
LORA_NODE_ADDR  = 0         # gateway node-address
LORA_ACK_DELAY  = 0.1       # delay time before sending ACK
LORA_TX_POWER   = 23        # transmit power (max: 23)

ACTIVE_WINDOW_START = 7     # active (online) window start hour
ACTIVE_WINDOW_END   = 17    # active (online) window end hour
                            # the gateway runs from <start>:00-<end>:59

# ----------------------------------------------------------------------------
# technical constants, don't change unless you know why

RECEIVE_TIMEOUT  = 1.0      # single receive wait-time
GET_TIME_REPEATS = 3        # how many times card.time() is executed
MAX_SYNC_TIME    = 300      # number of seconds to wait for a sync

# ----------------------------------------------------------------------------
# Development-mode (useful only for developers with a connected console)

DEV_MODE   = False
DEV_UPTIME = 300            # minimum uptime regardless of active window
DEV_SLEEP  =  60            # max sleep-time in DEV_MODE