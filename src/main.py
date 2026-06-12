#-----------------------------------------------------------------------------
# Basic data-collection program.
#
# The code is encapsulated in the class Datacollector, mainly to allow
# the use of precompiled code.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import datacollector

try:
  app = datacollector.DataCollector()
  app.run()
except Exception as ex:
  # log exception to /sd or /saves, if already mounted
  # memory could be scarce, so don't log too much
  import gc
  gc.collect()
  import traceback, storage
  logfile = None
  try:
    storage.getmount("/sd")
    logfile = "/sd/fatal_exception.log"
  except:
    try:
      storage.getmount("/saves")
      logfile = "/saves/fatal_exception.log"
    except:
      pass

  storage = None
  gc.collect()

  if logfile:
    with open(logfile,"at") as f:
      f.write("\n")
      traceback.print_exception(ex,file=f)
    # also try to log timestamp
    try:
      with open(logfile,"at") as f:
        f.write(f"at: {app.rtc.rtc_int.datetime}\n")
    except:
      pass

  # print exception to console in any case
  traceback.print_exception(ex)
  traceback = None
  gc.collect()

  # reset device
  import microcontroller
  if datacollector.g_config.TEST_MODE:
    import time
    print("===> Automatic reset in 5 seconds. Interrupt with CTRL-C")
    time.sleep(5)
  microcontroller.reset()
print("please press the reset-button!")
