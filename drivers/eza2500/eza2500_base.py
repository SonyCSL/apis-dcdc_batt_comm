# -*- coding: utf-8 -*-

from struct import *
from essx.essx_exception import *
import eza2500_util

class EZA2500CommandBase(object):
  """
  EZA2500の制御コマンドの基底となるクラス
  """
  def __init__(self, device = None):
    self.device = device

  def _recv(self):
    """
    deviceよりデータを受信する

    LENが期待通りでない場合は例外 ESSXValueException
    CMDが期待通りでない場合は例外 ESSXValueException
    チェックサムが期待通りでない場合は例外 ESSXChecksumException
    """
    while True:
      while True:
        recv_data0 = self.device.read(1)
        essx_debug.dump(recv_data0)
        if len(recv_data0) == 0:
          continue
        _sfd = ord(recv_data0)
        if _sfd == 2:
          break

      while True:
        recv_data1 = self.device.read(1)
        essx_debug.dump(recv_data1)
        if len(recv_data1) == 0:
          continue

        _len = ord(recv_data1)
        if _len == self.ACK_LEN or _len == self.NAK_LEN:
          #essx_debug.dump(recv_data0 + recv_data1)
          break
      if _len == self.ACK_LEN or _len == self.NAK_LEN:
        break

    recv_data2 = self.device.read(3)
    (_ad1, _ad2, _cmd) = unpack("BBB", recv_data2)
    res = {}
    res["sfd"] = _sfd
    res["len"] = _len
    res["ad1"] = _ad1
    res["ad2"] = _ad2
    res["cmd"] = _cmd

    if _cmd != self.COMMAND and _cmd != (self.COMMAND | 0x80):
      essx_debug.dump(recv_data0 + recv_data1 + recv_data2)
      raise ESSXValueException("cmd: %d != %d" % (_len, self.COMMAND))

    recv_data3 = self.device.read(_len + 2)
    recv_data = recv_data0 + recv_data1 + recv_data2 + recv_data3
    essx_debug.dump(recv_data2 + recv_data3)

    if eza2500_util.verify_check_sum(recv_data) == False:
      raise ESSXChecksumException("checksum error")

    return recv_data

#単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
if __name__  == "__main__":
  from struct import *
  import StringIO
  from eza2500_device import *
  from command0101 import *

  class DummySerial(object):
    def __init__(self):
      self.reader = StringIO.StringIO("\2\2\1\2\0\0\0\0\0")
      self.writer = StringIO.StringIO()
    def read(self, size):
      ret = self.reader.read(size)
      return ret
    def write(self, data):
      essx_debug.dump(data)
      self.writer.write(data)
      return len(data)

  # checksumが間違ったデータを受信したときに
  # ESSXChecksumExceptionが発生するか？
  dev = DummySerial()
  eza2500_dev = EZA2500Device(dev = dev, timeout = 1)
  b = Command0101(eza2500_dev)
  try:
    b._recv()
    print("ng")
  except ESSXChecksumException as e:
    print("1110 ok")

  # レスポンスのCMDが期待した値でないときに
  # ESSXValueExceptionが発生するか？
  # 1-1 (CMD=0)を送ったとに CMD=1でレスポンスがあった
  dev.reader = StringIO.StringIO("\2\2\1\2\1\0\0\3\0")
  b = Command0101(eza2500_dev)
  try:
    b._recv()
    print("ng")
  except ESSXValueException as e:
    print("1111 ok")

  # レスポンスのCMDが期待したNAK値のときに
  # 正常終了するか？
  dev.reader = StringIO.StringIO("\2\2\1\2\x80\0\0\x83\0")
  b = Command0101(eza2500_dev)
  b._recv()
  print("1113 ok")

  # レスポンスのCMDが期待したNAK値でないときに
  # ESSXValueExceptionが発生するか？
  # 1-1 (CMD=0)を送ったとに CMD=0x81でレスポンスがあった
  dev.reader = StringIO.StringIO("\2\2\1\2\x81\0\0\x84\0")
  b = Command0101(eza2500_dev)
  try:
    b._recv()
    print("ng")
  except ESSXValueException as e:
    print("1112 ok")



