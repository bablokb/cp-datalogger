#-----------------------------------------------------------------------------
# Base task for all receiver tasks (shared code).
# 
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

class BaseTask:
  def __init__(self, tools):
    """ constructor """
    self.tools = tools
