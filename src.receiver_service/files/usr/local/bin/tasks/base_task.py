#-----------------------------------------------------------------------------
# Base task for all receiver tasks (shared code).
# 
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

class BaseTask:

  # --- read configuration value   --------------------------------------------

  def _get_value(self,cparser,section,option,default):
    """ get value of config-variables and return given default if unset """

    if cparser.has_section(section):
      try:
        value = cparser.get(section,option)
      except:
        value = default
    else:
      value = default
    return value
