#-----------------------------------------------------------------------------
# Configuration for logging (template file).
# Adapt and copy to log_config.py (log_config.py is not tracked).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger

# default: log to console
g_logger = Logger('console')            # normal print-statements

# no logging
#g_logger = Logger(None)                 # disable logging

# log to sd-card
#g_logger = Logger('/sd/message.log')   # write to file (msg before mount are lost!)

# log to UART-serial
#import busio
#import pins
#uart = busio.UART(pins.PIN_TX, pins.PIN_RX, baudrate=115200)
#g_logger = Logger(uart)
