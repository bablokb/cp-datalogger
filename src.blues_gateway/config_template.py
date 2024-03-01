#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular. Configuration constants.
#
# Copy this file to config.py and modify according to your needs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# Development-mode (useful only with a connected console)
DEV_MODE = False

# action to perform when receiving data
#   None:  no action, just print to log
#   False: buffer data to notecard, but don't sync
#   True:  don't buffer data, sync to Notehub immediatly
SYNC_BLUES_ACTION = True
RECEIVE_TIMEOUT = 1.0       # single receive wait-time

LORA_FREQ       = 433.0     # frequency 433, 868, 915
LORA_NODE_ADDR  = 0         # gateway node-address
LORA_ACK_DELAY  = 0.1       # delay time before sending ACK
LORA_TX_POWER   = 23        # transmit power (max: 23)
