# -*- coding: utf-8 -*-
import sys
from essx_exception import ESSXException, ESSXTimeoutException, ESSXChecksumException, ESSXValueException, ESSXParameterException, ESSXDeviceException, ESSXFatalException, ESSXConfigException
from essx_debug import log, hexstr, dump, debug_log
from essx_global import ESSXGlobal

try:
  import essx_rs485 
except ImportError as err:
  sys.stderr.write("warning: cannot import essx_rs485\n")
except ImportError as err:
  sys.stderr.write("warning: cannot import essx_can\n")

try:
  import essx_modbus
except ImportError as err:
  sys.stderr.write("warning: cannot import essx_modbus\n")


__all__ = [
    "ESSXGlobal", "log", "hexstr", "dump", "debug_log",
    "ESSXException", "ESSXTimeoutException", "ESSXChecksumException",
    "ESSXValueException", "ESSXParameterException", "ESSXDeviceException",
    "ESSXFatalException", "ESSXConfigException",
    "essx_rs485", "essx_modbus"
]

