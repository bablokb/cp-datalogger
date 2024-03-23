#-----------------------------------------------------------------------------
# Basic data-collection program.
#
# The code is encapsulated in the class Datacollector, mainly to allow
# the use of precompiled code.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import gc
print(f"main: free memory at start: {gc.mem_free()}")

import datacollector
print(f"main: free memory after import datacollector: {gc.mem_free()}")

try:
  app = datacollector.DataCollector()
  app.run()
except Exception as ex:
  import traceback
  traceback.print_exception(ex)
  try:
    app.cleanup()
  except:
    pass
  print("please press the reset-button!")
