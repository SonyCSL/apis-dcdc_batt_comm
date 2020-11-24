# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
from eza2500 import eza2500_base
from eza2500 import eza2500_util

class Command0701(eza2500_base.EZA2500CommandBase):
  """ EZA2500 7-1 """

  COMMAND = 29
  CMD_LEN = 0
  ACK_LEN = 10
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0701, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,29) + b"00"
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
    if _cmd == 0x1d: #ACK
      (_bcf ,_cvb ,_dlb ,_cdb ,_ddb ,_chksum) = unpack("<HHHHHH", recv_data[5:])
      _cvb = eza2500_util.q_denormalize(_cvb, 14, '48', '32', '62', 'cvb')
      _dlb = eza2500_util.q_denormalize(_dlb, 14, '48', '32', '64', 'dlb')
      _cdb = eza2500_util.q_denormalize(_cdb, 14, '48', '0', '12', 'cdb')
      _ddb = eza2500_util.q_denormalize(_ddb, 14, '48', '0', '12', 'ddb')
      res["bcf"] = _bcf
      res["cvb"] = _cvb
      res["dlb"] = _dlb
      res["cdb"] = _cdb
      res["ddb"] = _ddb
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9d: #NAK
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
        _bcf = 0
        _cvb = 47.0
        _cvb = int(eza2500_util.q_normalize(_cvb, 14, '48', '32', '62', 'cvb'))
        _dlb = 48.0
        _dlb = int(eza2500_util.q_normalize(_dlb, 14, '48', '32', '64', 'dlb'))
        _cdb = 6.0
        _cdb = int(eza2500_util.q_normalize(_cdb, 14, '48', '0', '12', 'cdb'))
        _ddb = 6.0
        _ddb = int(eza2500_util.q_normalize(_ddb, 14, '48', '0', '12', 'ddb'))
        _chksum = 0
        data = pack("<BBBBBHHHHHH", 2, Command0701.ACK_LEN, 1, 2, 0x1d, _bcf ,_cvb ,_dlb ,_cdb ,_ddb ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0701(dev)
    if params == None:
      params = {}
    cmd.send(1, 2, params)
    cmd.recv()
class Command0704(eza2500_base.EZA2500CommandBase):
  """ EZA2500 7-4 """

  COMMAND = 29
  CMD_LEN = 10
  ACK_LEN = 10
  NAK_LEN = 2

  def __init__(self, device):
    super(Command0704, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    if 'bcf' in params:
      _bcf = params['bcf']
    else:
      raise ESSXParameterException('no parameter: bcf')
    if 'cvb' in params:
      _cvb = params['cvb']
    else:
      raise ESSXParameterException('no parameter: cvb')
    if 'dlb' in params:
      _dlb = params['dlb']
    else:
      raise ESSXParameterException('no parameter: dlb')
    if 'cdb' in params:
      _cdb = params['cdb']
    else:
      raise ESSXParameterException('no parameter: cdb')
    if 'ddb' in params:
      _ddb = params['ddb']
    else:
      raise ESSXParameterException('no parameter: ddb')
    _cvb = int(eza2500_util.q_normalize(_cvb, 14, '48', '32', '62', 'cvb'))
    _dlb = int(eza2500_util.q_normalize(_dlb, 14, '48', '32', '64', 'dlb'))
    _cdb = int(eza2500_util.q_normalize(_cdb, 14, '48', '0', '12', 'cdb'))
    _ddb = int(eza2500_util.q_normalize(_ddb, 14, '48', '0', '12', 'ddb'))
    req = pack("<BBBBBHHHHH", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,29 ,_bcf ,_cvb ,_dlb ,_cdb ,_ddb) + b"00"
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
    if _cmd == 0x1d: #ACK
      (_bcf ,_cvb ,_dlb ,_cdb ,_ddb ,_chksum) = unpack("<HHHHHH", recv_data[5:])
      _cvb = eza2500_util.q_denormalize(_cvb, 14, '48', '32', '62', 'cvb')
      _dlb = eza2500_util.q_denormalize(_dlb, 14, '48', '32', '64', 'dlb')
      _cdb = eza2500_util.q_denormalize(_cdb, 14, '48', '0', '12', 'cdb')
      _ddb = eza2500_util.q_denormalize(_ddb, 14, '48', '0', '12', 'ddb')
      res["bcf"] = _bcf
      res["cvb"] = _cvb
      res["dlb"] = _dlb
      res["cdb"] = _cdb
      res["ddb"] = _ddb
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x9d: #NAK
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
        _bcf = 0
        _cvb = 47.0
        _cvb = int(eza2500_util.q_normalize(_cvb, 14, '48', '32', '62', 'cvb'))
        _dlb = 48.0
        _dlb = int(eza2500_util.q_normalize(_dlb, 14, '48', '32', '64', 'dlb'))
        _cdb = 6.0
        _cdb = int(eza2500_util.q_normalize(_cdb, 14, '48', '0', '12', 'cdb'))
        _ddb = 6.0
        _ddb = int(eza2500_util.q_normalize(_ddb, 14, '48', '0', '12', 'ddb'))
        _chksum = 0
        data = pack("<BBBBBHHHHHH", 2, Command0704.ACK_LEN, 1, 2, 0x1d, _bcf ,_cvb ,_dlb ,_cdb ,_ddb ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command0704(dev)
    if params == None:
      params = {}
      _bcf = 0
      params['bcf'] = _bcf
      _cvb = 47.0
      params['cvb'] = _cvb
      _dlb = 48.0
      params['dlb'] = _dlb
      _cdb = 6.0
      params['cdb'] = _cdb
      _ddb = 6.0
      params['ddb'] = _ddb
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
    Command0701.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
  try:
    Command0704.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
