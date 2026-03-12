#-----------------------------------------------------------------------------
# Makefile configuration for Datalogger Adafruit PicowBell
#
# Website: https://github.com/cp-datalogger
#-----------------------------------------------------------------------------

# path to hardware configuration file
PCB=examples/picowbell_adalogger/pins.py

# target deployment directory
DEPLOY_TO=picowbell_adalogger.local

# application configuration
CONFIG=examples/picowbell_adalogger/config.py

# log configuration
LOG_CONFIG=examples/log_config_console.py

# AP configuration
AP_CONFIG=examples/ap_config_prod.py
