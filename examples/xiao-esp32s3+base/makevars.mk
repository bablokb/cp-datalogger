#-----------------------------------------------------------------------------
# Makefile configuration for Datalogger XIAO ESP32S3 + XIAO-Base
#
# Website: https://github.com/cp-datalogger
#-----------------------------------------------------------------------------

# path to hardware configuration file
PCB=examples/xiao-esp32s3+base/pins.py

# target deployment directory
DEPLOY_TO=xiao-esp32s3+base.local

# application configuration
CONFIG=examples/xiao-esp32s3+base/config.py

# log configuration
LOG_CONFIG=examples/xiao-esp32s3+base/log_config_console.py

# AP configuration (ignored)
AP_CONFIG=examples/xiao-esp32s3+base/ap_config_prod.py

# don't build the admin-interface
ADMIN=0
