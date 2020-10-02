# -*- coding: utf-8 -*-
import datetime
import serial
import time
import os
from essx.essx_exception import *
from essx import essx_debug
import eza_device

class EZA2500Device(eza_device.EZADevice):
  """
  EZA2500と通信をするクラス

  @param dev 通信デバイス read / writeが実装されていること
  @param timeout タイムアウト時間。read / writeでこの時間を経過するとESSXTimeoutException
  """

  def __init__(self, dev = None, timeout = None):
    self.ser = dev #
    self.ser.timeout = 0.01
    self.timeout = timeout


#単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
if __name__  == "__main__":
  from struct import *
  import StringIO

  class DummySerial(object):
    def __init__(self):
      self.reader = StringIO.StringIO("ABCDEFG")
      self.writer = StringIO.StringIO()
    def read(self, size):
      ret = self.reader.read(size)
      return ret
    def write(self, data):
      essx_debug.dump(data)
      self.writer.write(data)
      return len(data)

  #ser_dev = serial.Serial("/dev/cuaU1", 115200, timeout = 0.01)
  eza2500_dev = EZA2500Device(dev = DummySerial(), timeout = 1)
  wdata = pack("<BBBBBH", 5, 0, 0x31, 0x32, 0, 0x31 + 0x32)
  eza2500_dev.write(wdata)
  print '201 ok'
  essx_debug.dump(eza2500_dev.read(7)) #=> no timeout
  print '202 ok'
  try:
    essx_debug.dump(eza2500_dev.read(7)) #=> timeout
    raise ESSXFatalException("fatal")
  except ESSXTimeoutException as e:
    print "203 ok"

