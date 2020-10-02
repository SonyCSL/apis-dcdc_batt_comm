# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command1201(eza2500_base.EZA2500CommandBase):
  """ EZA2500 12-1 """

  COMMAND = 13
  CMD_LEN = 0
  ACK_LEN = 16
  NAK_LEN = 2

  def __init__(self, device):
    super(Command1201, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,13) + "00"
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
    if _cmd == 0x0d: #ACK
      (_vgq ,_igq ,_vbq ,_ibq ,_wgq ,_wbq ,_icq ,_tmpq ,_chksum) = unpack("<HHHHHHHHH", recv_data[5:])
      res["vgq"] = _vgq
      res["igq"] = _igq
      res["vbq"] = _vbq
      res["ibq"] = _ibq
      res["wgq"] = _wgq
      res["wbq"] = _wbq
      res["icq"] = _icq
      res["tmpq"] = _tmpq
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x8d: #NAK
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
        _vgq = 0
        _igq = 0
        _vbq = 0
        _ibq = 0
        _wgq = 0
        _wbq = 0
        _icq = 0
        _tmpq = 0
        _chksum = 0
        data = pack("<BBBBBHHHHHHHHH", 2, Command1201.ACK_LEN, 1, 2, 0x0d, _vgq ,_igq ,_vbq ,_ibq ,_wgq ,_wbq ,_icq ,_tmpq ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command1201(dev)
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
    Command1201.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
