# -*- coding: utf-8 -*-
import datetime
import serial
import time
import os
from essx.essx_exception import *
from essx import essx_debug


class EZADevice:
  """
  EZAと通信をするクラス

  @param dev 通信デバイス read / writeが実装されていること
  @param timeout タイムアウト時間。read / writeでこの時間を経過するとESSXTimeoutException
  """

  def __init__(self, dev = None, timeout = None):
    self.ser = dev #
    self.ser.timeout = 0.01
    self.timeout = timeout

  def read(self, size):
    """
    データを読む。
    timeoutで指定した時間が経過するまでデータが読めない場合 ESSXTimeoutExceptionが発生する。

    @param size バイト数
    @return バイトデータ
    """
    if self.timeout != None:
      expired = datetime.datetime.now() + datetime.timedelta(seconds = self.timeout)
    else:
      expired = None

    res = b''
    while True:
      read_data = self.ser.read(size)
      res += read_data
      size -= len(read_data)
      if size <= 0:
        break
      if expired != None and datetime.datetime.now() >= expired:
        raise ESSXTimeoutException("read timeout")

    time.sleep(2.0 / 1000) #wait 2msec
    return res

  def write(self, data, size = None):
    """
    sizeで指定したバイトのデータに書く。
    timeoutで指定した時間が経過するまでデータが書けない場合 ESSXTimeoutExceptionが発生する。

    @param data データ
    @param size サイズ。省略した場合はデータ全て
    @return サイズ
    """
    if self.timeout != None:
      expired = datetime.datetime.now() + datetime.timedelta(seconds = self.timeout)
    else:
      expired = None

    if size == None:
      size = len(data)
    size0 = size

    while True:
      write_size = self.ser.write(data)
      size -= write_size
      if size <= 0:
        break
      if expired != None and datetime.datetime.now() >= expired:
        raise ESSXTimeoutException("write timeout")
      data = data[write_size:]

    return size0

#単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
if __name__  == "__main__":
  from struct import *
  from io import BytesIO

  class DummySerial(object):
    def __init__(self):
      self.reader = BytesIO(b"ABCDEFG")
      self.writer = BytesIO()
    def read(self, size):
      ret = self.reader.read(size)
      return ret
    def write(self, data):
      essx_debug.dump(data)
      self.writer.write(data)
      return len(data)

  #ser_dev = serial.Serial("/dev/cuaU1", 115200, timeout = 0.01)
  eza_dev = EZADevice(dev = DummySerial(), timeout = 1)
  wdata = pack("<BBBBBH", 5, 0, 0x31, 0x32, 0, 0x31 + 0x32)
  eza_dev.write(wdata)
  print('201 ok')
  essx_debug.dump(eza_dev.read(7)) #=> no timeout
  print('202 ok')
  try:
    essx_debug.dump(eza_dev.read(7)) #=> timeout
    raise ESSXFatalException("fatal")
  except ESSXTimeoutException as e:
    print('203 ok')

