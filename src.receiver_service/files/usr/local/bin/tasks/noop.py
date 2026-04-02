#-----------------------------------------------------------------------------
# Receiver task: noop
# 
# This task does nothing.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from .base_task import BaseTask

class NOOP(BaseTask):
  def __init__(self, tools):
    """ constructor """
    super().__init__(tools)

  def run(self, record):
    """ execute task (no operation) """
    pass
