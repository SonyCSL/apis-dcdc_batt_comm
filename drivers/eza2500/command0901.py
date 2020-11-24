# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
from eza2500 import eza2500_base
from eza2500 import eza2500_util

class Command0901(eza2500_base.EZA2500CommandBase):
  """ EZA2500 9-1 """

  COMMAND = 18
  CMD_LEN = 0
  ACK_LEN = 6
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0901, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,18) + b"00"
    return eza2500_util.replace_check_sum(req)

  def send(self, ad1, ad2, params = {}):
    send_data = self.pack_senddata(ad1, ad2, params)
    essx_debug.log('send')
    essx_debug.dump(send_data)
    self.device.write(send_data)
    return send_data

  def recv(self):
    essx_debug.log('recv')
    recv_data = self._recv()

    self.response_raw = recv_data
    res = {}
    (_sfd, _len, _ad1, _ad2, _cmd) = unpack("BBBBB", recv_data[0:5])
    if _cmd == 0x12: #ACK
      (_alm1 ,_alm2 ,_alm3 ,_chksum) = unpack("<HHHH", recv_data[5:])
      res["alm1"] = _alm1
      res["alm2"] = _alm2
      res["alm3"] = _alm3
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x92: #NAK
      (_ercd ,_chksum) = unpack("<HH", recv_data[5:])
      res["ercd"] = _ercd
      res["chksum"] = _chksum
      self.response = res
      raise ESSXDeviceException("error: ERCD=%x" % _ercd)
    else:
      raise ESSXValueException("bad response")

    self.response = res
    essx_debug.log('recv')
    #essx_debug.dump(recv_data)
    return recv_data

  @classmethod
  def unit_test(cls, dev = None, params = None):
    from io import BytesIO

    class Dummy:
      def __init__(self):
        _alm1 = 0
        _alm2 = 0
        _alm3 = 0
        _chksum = 0
        data = pack("<BBBBBHHHH", 2, Command0901.ACK_LEN, 1, 2, 0x12, _alm1 ,_alm2 ,_alm3 ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0901(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0904(eza2500_base.EZA2500CommandBase):
  """ EZA2500 9-4 """

  COMMAND = 18
  CMD_LEN = 2
  ACK_LEN = 2
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0904, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'd0' in params:
      _d0 = params['d0']
    else:
      raise ESSXParameterException('no parameter: d0')
    if 'd1' in params:
      _d1 = params['d1']
    else:
      raise ESSXParameterException('no parameter: d1')
    req = pack("<BBBBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,18 ,_d0 ,_d1) + b"00"
    return eza2500_util.replace_check_sum(req)

  def send(self, ad1, ad2, params = {}):
    send_data = self.pack_senddata(ad1, ad2, params)
    essx_debug.log('send')
    essx_debug.dump(send_data)
    self.device.write(send_data)
    return send_data

  def recv(self):
    essx_debug.log('recv')
    recv_data = self._recv()

    self.response_raw = recv_data
    res = {}
    (_sfd, _len, _ad1, _ad2, _cmd) = unpack("BBBBB", recv_data[0:5])
    if _cmd == 0x12: #ACK
      (_d0 ,_d1 ,_chksum) = unpack("<BBH", recv_data[5:])
      res["d0"] = _d0
      res["d1"] = _d1
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x92: #NAK
      (_ercd ,_chksum) = unpack("<HH", recv_data[5:])
      res["ercd"] = _ercd
      res["chksum"] = _chksum
      self.response = res
      raise ESSXDeviceException("error: ERCD=%x" % _ercd)
    else:
      raise ESSXValueException("bad response")

    self.response = res
    essx_debug.log('recv')
    #essx_debug.dump(recv_data)
    return recv_data

  @classmethod
  def unit_test(cls, dev = None, params = None):
    from io import BytesIO

    class Dummy:
      def __init__(self):
        _d0 = 0
        _d1 = 0
        _chksum = 0
        data = pack("<BBBBBBBH", 2, Command0904.ACK_LEN, 1, 2, 0x12, _d0 ,_d1 ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0904(dev)
    if params == None:
      params = {}
      _d0 = 0
      params['d0'] = _d0
      _d1 = 0
      params['d1'] = _d1
    cmd.send(1, 2, params)
    cmd.recv()

#単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
if __name__  == "__main__":
  import sys
  #import serial
  import essx
  from eza2500_device import EZA2500Device

  if len(sys.argv) > 1 and sys.argv[1] == '1':
    ser_dev = essx.essx_rs232c.ESSXRS232C('/dev/cuaU1', 115200)
    dev = EZA2500Device(dev = ser_dev, timeout = 1)
  else:
    dev = None
  try:
    Command0901.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0904.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
