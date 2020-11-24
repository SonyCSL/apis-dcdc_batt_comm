# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
from eza2500 import eza2500_base
from eza2500 import eza2500_util

class Command0601(eza2500_base.EZA2500CommandBase):
  """ EZA2500 6-1 """

  COMMAND = 28
  CMD_LEN = 0
  ACK_LEN = 12
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0601, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,28) + b"00"
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
    if _cmd == 0x1c: #ACK
      (_cib ,_dig ,_ubv ,_ugv ,_obv ,_ogv ,_chksum) = unpack("<HHHHHHH", recv_data[5:])
      _cib = eza2500_util.q_denormalize(_cib, 13, '52.08', '0', '56.77', 'cib')
      _dig = eza2500_util.q_denormalize(_dig, 13, '7.8125', '0', '8.5162', 'dig')
      _ubv = eza2500_util.q_denormalize(_ubv, 14, '48', '32', '68', 'ubv')
      _ugv = eza2500_util.q_denormalize(_ugv, 14, '380', '260', '425', 'ugv')
      _obv = eza2500_util.q_denormalize(_obv, 14, '48', '32', '68', 'obv')
      _ogv = eza2500_util.q_denormalize(_ogv, 14, '380', '260', '425', 'ogv')
      res["cib"] = _cib
      res["dig"] = _dig
      res["ubv"] = _ubv
      res["ugv"] = _ugv
      res["obv"] = _obv
      res["ogv"] = _ogv
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9c: #NAK
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
        _cib = 28.385
        _cib = int(eza2500_util.q_normalize(_cib, 13, '52.08', '0', '56.77', 'cib'))
        _dig = 4.2581
        _dig = int(eza2500_util.q_normalize(_dig, 13, '7.8125', '0', '8.5162', 'dig'))
        _ubv = 50.0
        _ubv = int(eza2500_util.q_normalize(_ubv, 14, '48', '32', '68', 'ubv'))
        _ugv = 342.5
        _ugv = int(eza2500_util.q_normalize(_ugv, 14, '380', '260', '425', 'ugv'))
        _obv = 50.0
        _obv = int(eza2500_util.q_normalize(_obv, 14, '48', '32', '68', 'obv'))
        _ogv = 342.5
        _ogv = int(eza2500_util.q_normalize(_ogv, 14, '380', '260', '425', 'ogv'))
        _chksum = 0
        data = pack("<BBBBBHHHHHHH", 2, Command0601.ACK_LEN, 1, 2, 0x1c, _cib ,_dig ,_ubv ,_ugv ,_obv ,_ogv ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0601(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0604(eza2500_base.EZA2500CommandBase):
  """ EZA2500 6-4 """

  COMMAND = 28
  CMD_LEN = 12
  ACK_LEN = 12
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0604, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'cib' in params:
      _cib = params['cib']
    else:
      raise ESSXParameterException('no parameter: cib')
    if 'dig' in params:
      _dig = params['dig']
    else:
      raise ESSXParameterException('no parameter: dig')
    if 'ubv' in params:
      _ubv = params['ubv']
    else:
      raise ESSXParameterException('no parameter: ubv')
    if 'ugv' in params:
      _ugv = params['ugv']
    else:
      raise ESSXParameterException('no parameter: ugv')
    if 'obv' in params:
      _obv = params['obv']
    else:
      raise ESSXParameterException('no parameter: obv')
    if 'ogv' in params:
      _ogv = params['ogv']
    else:
      raise ESSXParameterException('no parameter: ogv')
    _cib = int(eza2500_util.q_normalize(_cib, 13, '52.08', '0', '56.77', 'cib'))
    _dig = int(eza2500_util.q_normalize(_dig, 13, '7.8125', '0', '8.5162', 'dig'))
    _ubv = int(eza2500_util.q_normalize(_ubv, 14, '48', '32', '68', 'ubv'))
    _ugv = int(eza2500_util.q_normalize(_ugv, 14, '380', '260', '425', 'ugv'))
    _obv = int(eza2500_util.q_normalize(_obv, 14, '48', '32', '68', 'obv'))
    _ogv = int(eza2500_util.q_normalize(_ogv, 14, '380', '260', '425', 'ogv'))
    req = pack("<BBBBBHHHHHH", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,28 ,_cib ,_dig ,_ubv ,_ugv ,_obv ,_ogv) + b"00"
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
    if _cmd == 0x1c: #ACK
      (_cib ,_dig ,_ubv ,_ugv ,_obv ,_ogv ,_chksum) = unpack("<HHHHHHH", recv_data[5:])
      _cib = eza2500_util.q_denormalize(_cib, 13, '52.08', '0', '56.77', 'cib')
      _dig = eza2500_util.q_denormalize(_dig, 13, '7.8125', '0', '8.5162', 'dig')
      _ubv = eza2500_util.q_denormalize(_ubv, 14, '48', '32', '68', 'ubv')
      _ugv = eza2500_util.q_denormalize(_ugv, 14, '380', '260', '425', 'ugv')
      _obv = eza2500_util.q_denormalize(_obv, 14, '48', '32', '68', 'obv')
      _ogv = eza2500_util.q_denormalize(_ogv, 14, '380', '260', '425', 'ogv')
      res["cib"] = _cib
      res["dig"] = _dig
      res["ubv"] = _ubv
      res["ugv"] = _ugv
      res["obv"] = _obv
      res["ogv"] = _ogv
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9c: #NAK
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
        _cib = 28.385
        _cib = int(eza2500_util.q_normalize(_cib, 13, '52.08', '0', '56.77', 'cib'))
        _dig = 4.2581
        _dig = int(eza2500_util.q_normalize(_dig, 13, '7.8125', '0', '8.5162', 'dig'))
        _ubv = 50.0
        _ubv = int(eza2500_util.q_normalize(_ubv, 14, '48', '32', '68', 'ubv'))
        _ugv = 342.5
        _ugv = int(eza2500_util.q_normalize(_ugv, 14, '380', '260', '425', 'ugv'))
        _obv = 50.0
        _obv = int(eza2500_util.q_normalize(_obv, 14, '48', '32', '68', 'obv'))
        _ogv = 342.5
        _ogv = int(eza2500_util.q_normalize(_ogv, 14, '380', '260', '425', 'ogv'))
        _chksum = 0
        data = pack("<BBBBBHHHHHHH", 2, Command0604.ACK_LEN, 1, 2, 0x1c, _cib ,_dig ,_ubv ,_ugv ,_obv ,_ogv ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0604(dev)
    if params == None:
      params = {}
      _cib = 28.385
      params['cib'] = _cib
      _dig = 4.2581
      params['dig'] = _dig
      _ubv = 50.0
      params['ubv'] = _ubv
      _ugv = 342.5
      params['ugv'] = _ugv
      _obv = 50.0
      params['obv'] = _obv
      _ogv = 342.5
      params['ogv'] = _ogv
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
    Command0601.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0604.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
