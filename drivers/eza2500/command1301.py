# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command1301(eza2500_base.EZA2500CommandBase):
  """ EZA2500 13-1 """

  COMMAND = 14
  CMD_LEN = 0
  ACK_LEN = 16
  NAK_LEN = 2

  def __init__(self, device):
    super(Command1301, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,14) + "00"
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
    if _cmd == 0x0e: #ACK
      (_tsq ,_tpq ,_v5q ,_fn1q ,_fn2q ,_fn3q ,_fn4q ,_fn5q ,_chksum) = unpack("<HHHHHHHHH", recv_data[5:])
      res["tsq"] = _tsq
      res["tpq"] = _tpq
      res["v5q"] = _v5q
      res["fn1q"] = _fn1q
      res["fn2q"] = _fn2q
      res["fn3q"] = _fn3q
      res["fn4q"] = _fn4q
      res["fn5q"] = _fn5q
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x8e: #NAK
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
        _tsq = 0
        _tpq = 0
        _v5q = 0
        _fn1q = 0
        _fn2q = 0
        _fn3q = 0
        _fn4q = 0
        _fn5q = 0
        _chksum = 0
        data = pack("<BBBBBHHHHHHHHH", 2, Command1301.ACK_LEN, 1, 2, 0x0e, _tsq ,_tpq ,_v5q ,_fn1q ,_fn2q ,_fn3q ,_fn4q ,_fn5q ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command1301(dev)
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
    Command1301.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
