# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command0401(eza2500_base.EZA2500CommandBase):
  """ EZA2500 4-1 """

  COMMAND = 26
  CMD_LEN = 0
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0401, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,26) + "00"
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
    if _cmd == 0x1a: #ACK
      (_dvg ,_drg ,_chksum) = unpack("<HHH", recv_data[5:])
      _dvg = eza2500_util.q_denormalize(_dvg, 14, '380', '260', '390', 'dvg')
      _drg = eza2500_util.q_denormalize(_drg, 13, '1', '0', '3.999', 'drg')
      res["dvg"] = _dvg
      res["drg"] = _drg
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9a: #NAK
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
        _dvg = 325.0
        _dvg = int(eza2500_util.q_normalize(_dvg, 14, '380', '260', '390', 'dvg'))
        _drg = 1.9995
        _drg = int(eza2500_util.q_normalize(_drg, 13, '1', '0', '3.999', 'drg'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0401.ACK_LEN, 1, 2, 0x1a, _dvg ,_drg ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0401(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0404(eza2500_base.EZA2500CommandBase):
  """ EZA2500 4-4 """

  COMMAND = 26
  CMD_LEN = 4
  ACK_LEN = 4
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0404, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'dvg' in params:
      _dvg = params['dvg']
    else:
      raise ESSXParameterException('no parameter: dvg')
    if 'drg' in params:
      _drg = params['drg']
    else:
      raise ESSXParameterException('no parameter: drg')
    _dvg = int(eza2500_util.q_normalize(_dvg, 14, '380', '260', '390', 'dvg'))
    _drg = int(eza2500_util.q_normalize(_drg, 13, '1', '0', '3.999', 'drg'))
    req = pack("<BBBBBHH", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,26 ,_dvg ,_drg) + "00"
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
    if _cmd == 0x1a: #ACK
      (_dvg ,_drg ,_chksum) = unpack("<HHH", recv_data[5:])
      _dvg = eza2500_util.q_denormalize(_dvg, 14, '380', '260', '390', 'dvg')
      _drg = eza2500_util.q_denormalize(_drg, 13, '1', '0', '3.999', 'drg')
      res["dvg"] = _dvg
      res["drg"] = _drg
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9a: #NAK
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
        _dvg = 325.0
        _dvg = int(eza2500_util.q_normalize(_dvg, 14, '380', '260', '390', 'dvg'))
        _drg = 1.9995
        _drg = int(eza2500_util.q_normalize(_drg, 13, '1', '0', '3.999', 'drg'))
        _chksum = 0
        data = pack("<BBBBBHHH", 2, Command0404.ACK_LEN, 1, 2, 0x1a, _dvg ,_drg ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0404(dev)
    if params == None:
      params = {}
      _dvg = 325.0
      params['dvg'] = _dvg
      _drg = 1.9995
      params['drg'] = _drg
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
    Command0401.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0404.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
