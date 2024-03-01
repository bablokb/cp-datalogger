#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular.
#
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import gateway

try:
  app = gateway.Gateway()
  app.run()
except Exception as ex:
  import traceback
  traceback.print_exception(ex)
  try:
    app.cleanup()
  except:
    pass
  print("please press the reset-button!")
