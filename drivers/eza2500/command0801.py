# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command0801(eza2500_base.EZA2500CommandBase):
  """ EZA2500 8-1 """

  COMMAND = 22
  CMD_LEN = 0
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0801, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,22) + "00"
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
    if _cmd == 0x16: #ACK
      (_ccr ,_ddr ,_chksum) = unpack("<HHH", recv_data[5:])
      _ccr = eza2500_util.q_denormalize(_ccr, 14, '48', '0', '12', 'ccr')
      _ddr = eza2500_util.q_denormalize(_ddr, 14, '48', '0', '12', 'ddr')
      res["ccr"] = _ccr
      res["ddr"] = _ddr
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x96: #NAK
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
    import StringIO

    class Dummy:
      def __init__(self):
        _ccr = 6.0
        _ccr = int(eza2500_util.q_normalize(_ccr, 14, '48', '0', '12', 'ccr'))
        _ddr = 6.0
        _ddr = int(eza2500_util.q_normalize(_ddr, 14, '48', '0', '12', 'ddr'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0801.ACK_LEN, 1, 2, 0x16, _ccr ,_ddr ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0801(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0804(eza2500_base.EZA2500CommandBase):
  """ EZA2500 8-4 """

  COMMAND = 22
  CMD_LEN = 4
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0804, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'ccr' in params:
      _ccr = params['ccr']
    else:
      raise ESSXParameterException('no parameter: ccr')
    if 'ddr' in params:
      _ddr = params['ddr']
    else:
      raise ESSXParameterException('no parameter: ddr')
    _ccr = int(eza2500_util.q_normalize(_ccr, 14, '48', '0', '12', 'ccr'))
    _ddr = int(eza2500_util.q_normalize(_ddr, 14, '48', '0', '12', 'ddr'))
    req = pack("<BBBBBHH", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,22 ,_ccr ,_ddr) + "00"
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
    if _cmd == 0x16: #ACK
      (_ccr ,_ddr ,_chksum) = unpack("<HHH", recv_data[5:])
      _ccr = eza2500_util.q_denormalize(_ccr, 14, '48', '0', '12', 'ccr')
      _ddr = eza2500_util.q_denormalize(_ddr, 14, '48', '0', '12', 'ddr')
      res["ccr"] = _ccr
      res["ddr"] = _ddr
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x96: #NAK
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
    import StringIO

    class Dummy:
      def __init__(self):
        _ccr = 6.0
        _ccr = int(eza2500_util.q_normalize(_ccr, 14, '48', '0', '12', 'ccr'))
        _ddr = 6.0
        _ddr = int(eza2500_util.q_normalize(_ddr, 14, '48', '0', '12', 'ddr'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0804.ACK_LEN, 1, 2, 0x16, _ccr ,_ddr ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0804(dev)
    if params == None:
      params = {}
      _ccr = 6.0
      params['ccr'] = _ccr
      _ddr = 6.0
      params['ddr'] = _ddr
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
    Command0801.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0804.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
