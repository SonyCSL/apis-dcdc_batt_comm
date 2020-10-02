# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command0501(eza2500_base.EZA2500CommandBase):
  """ EZA2500 5-1 """

  COMMAND = 23
  CMD_LEN = 0
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0501, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,23) + "00"
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
    if _cmd == 0x17: #ACK
      (_pdz ,_mdz ,_chksum) = unpack("<HHH", recv_data[5:])
      _pdz = eza2500_util.q_denormalize(_pdz, 14, '380', '0', '57', 'pdz')
      _mdz = eza2500_util.q_denormalize(_mdz, 14, '380', '0', '57', 'mdz')
      res["pdz"] = _pdz
      res["mdz"] = _mdz
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x97: #NAK
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
        _pdz = 28.5
        _pdz = int(eza2500_util.q_normalize(_pdz, 14, '380', '0', '57', 'pdz'))
        _mdz = 28.5
        _mdz = int(eza2500_util.q_normalize(_mdz, 14, '380', '0', '57', 'mdz'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0501.ACK_LEN, 1, 2, 0x17, _pdz ,_mdz ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0501(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0504(eza2500_base.EZA2500CommandBase):
  """ EZA2500 5-4 """

  COMMAND = 23
  CMD_LEN = 4
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0504, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'pdz' in params:
      _pdz = params['pdz']
    else:
      raise ESSXParameterException('no parameter: pdz')
    if 'mdz' in params:
      _mdz = params['mdz']
    else:
      raise ESSXParameterException('no parameter: mdz')
    _pdz = int(eza2500_util.q_normalize(_pdz, 14, '380', '0', '57', 'pdz'))
    _mdz = int(eza2500_util.q_normalize(_mdz, 14, '380', '0', '57', 'mdz'))
    req = pack("<BBBBBHH", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,23 ,_pdz ,_mdz) + "00"
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
    if _cmd == 0x17: #ACK
      (_pdz ,_mdz ,_chksum) = unpack("<HHH", recv_data[5:])
      _pdz = eza2500_util.q_denormalize(_pdz, 14, '380', '0', '57', 'pdz')
      _mdz = eza2500_util.q_denormalize(_mdz, 14, '380', '0', '57', 'mdz')
      res["pdz"] = _pdz
      res["mdz"] = _mdz
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x97: #NAK
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
        _pdz = 28.5
        _pdz = int(eza2500_util.q_normalize(_pdz, 14, '380', '0', '57', 'pdz'))
        _mdz = 28.5
        _mdz = int(eza2500_util.q_normalize(_mdz, 14, '380', '0', '57', 'mdz'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0504.ACK_LEN, 1, 2, 0x17, _pdz ,_mdz ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0504(dev)
    if params == None:
      params = {}
      _pdz = 28.5
      params['pdz'] = _pdz
      _mdz = 28.5
      params['mdz'] = _mdz
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
    Command0501.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0504.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
