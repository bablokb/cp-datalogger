#-----------------------------------------------------------------------------
# Make configuration. Change PCB= to the correct version.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

PCB=v2
DEPLOY_TO=GW.local
CONFIG=configs.local/GW/config.py
AP_CONFIG=configs.local/GW/ap_config.py
SECRETS=configs.local/secrets.py

# Alternative log-configurations, choose one.
#   console: needs an attached PC, makes no sense otherwise
#   none:    most efficient
#   sd:      log to SD-card. For ex-post analysis of problems

LOG_CONFIG=configs.local/log_config_console.py
#LOG_CONFIG=configs.local/log_config_none.py
#LOG_CONFIG=configs.local/log_config_sd.py
