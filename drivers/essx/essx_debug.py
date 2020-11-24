# -*- coding: utf-8 -*-
import os

def _log(msg, level = 7):
  if 'ESSX_LOG_LEVEL' in os.environ:
    if int(os.environ['ESSX_LOG_LEVEL']) >= level:
      print(msg)
  else:
    return 0

def log(str, level = 7):
  _log(str, level)

def hexstr(data):
  a = []
  for i in range(len(data)):
    a.append("%02x" % data[i])

  return " ".join(a)

def dump(data, level = 7):
  _log(('%4d : %s' % (len(data), hexstr(data))), level)

def debug_log(s, level = 7):
  _log(str(s), level)


