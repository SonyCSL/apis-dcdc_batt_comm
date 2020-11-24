# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
from eza2500 import eza2500_base
from eza2500 import eza2500_util

class Command1101(eza2500_base.EZA2500CommandBase):
  """ EZA2500 11-1 """

  COMMAND = 10
  CMD_LEN = 0
  ACK_LEN = 16
  NAK_LEN = 2

  def __init__(self, device):
    super(Command1101, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,10) + b"00"
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
    if _cmd == 0x0a: #ACK
      (_ts ,_tp ,_v5s ,_fan1 ,_fan2 ,_fan3 ,_fan4 ,_fan5 ,_chksum) = unpack("<hhhhhhhhH", recv_data[5:])
      _v5s = eza2500_util.q_denormalize(_v5s, 10, '1', 'None', 'None', 'v5s')
      _fan1 = eza2500_util.q_denormalize(_fan1, 0, '1', 'None', 'None', 'fan1')
      _fan2 = eza2500_util.q_denormalize(_fan2, 0, '1', 'None', 'None', 'fan2')
      _fan3 = eza2500_util.q_denormalize(_fan3, 0, '1', 'None', 'None', 'fan3')
      _fan4 = eza2500_util.q_denormalize(_fan4, 0, '1', 'None', 'None', 'fan4')
      _fan5 = eza2500_util.q_denormalize(_fan5, 0, '1', 'None', 'None', 'fan5')
      res["ts"] = _ts
      res["tp"] = _tp
      res["v5s"] = _v5s
      res["fan1"] = _fan1
      res["fan2"] = _fan2
      res["fan3"] = _fan3
      res["fan4"] = _fan4
      res["fan5"] = _fan5
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x8a: #NAK
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
        _ts = 0
        _tp = 0
        _v5s = 0.0
        _v5s = int(eza2500_util.q_normalize(_v5s, 10, '1', 'None', 'None', 'v5s'))
        _fan1 = 0.0
        _fan1 = int(eza2500_util.q_normalize(_fan1, 0, '1', 'None', 'None', 'fan1'))
        _fan2 = 0.0
        _fan2 = int(eza2500_util.q_normalize(_fan2, 0, '1', 'None', 'None', 'fan2'))
        _fan3 = 0.0
        _fan3 = int(eza2500_util.q_normalize(_fan3, 0, '1', 'None', 'None', 'fan3'))
        _fan4 = 0.0
        _fan4 = int(eza2500_util.q_normalize(_fan4, 0, '1', 'None', 'None', 'fan4'))
        _fan5 = 0.0
        _fan5 = int(eza2500_util.q_normalize(_fan5, 0, '1', 'None', 'None', 'fan5'))
        _chksum = 0
        data = pack("<BBBBBhhhhhhhhH", 2, Command1101.ACK_LEN, 1, 2, 0x0a, _ts ,_tp ,_v5s ,_fan1 ,_fan2 ,_fan3 ,_fan4 ,_fan5 ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = BytesIO(data[:-2] + pack('BB', _chksum % 256, _chksum // 256))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command1101(dev)
    if params == None:
      params = {}
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
    Command1101.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
