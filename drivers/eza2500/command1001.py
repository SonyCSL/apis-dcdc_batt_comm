# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

class Command1001(eza2500_base.EZA2500CommandBase):
  """ EZA2500 10-1 """

  COMMAND = 9
  CMD_LEN = 0
  ACK_LEN = 16
  NAK_LEN = 2

  def __init__(self, device):
    super(Command1001, self).__init__(device)
    self.response = {}

  def pack_senddata(self, ad1, ad2, params = {}):
    req = pack("<BBBBB", 0x05 ,self.CMD_LEN ,ad1 ,ad2 ,9) + "00"
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
    if _cmd == 0x09: #ACK
      (_vg ,_ig ,_vb ,_ib ,_wg ,_wb ,_ic ,_tmp ,_chksum) = unpack("<hhhhhhhhH", recv_data[5:])
      _vg = eza2500_util.q_denormalize(_vg, 14, '380', 'None', 'None', 'vg')
      _ig = eza2500_util.q_denormalize(_ig, 13, '7.8125', 'None', 'None', 'ig')
      _vb = eza2500_util.q_denormalize(_vb, 14, '48', 'None', 'None', 'vb')
      _ib = eza2500_util.q_denormalize(_ib, 13, '52.08', 'None', 'None', 'ib')
      _wg = eza2500_util.q_denormalize(_wg, 11, '2500', 'None', 'None', 'wg')
      _wb = eza2500_util.q_denormalize(_wb, 11, '2500', 'None', 'None', 'wb')
      _tmp = eza2500_util.q_denormalize(_tmp, 7, '1', 'None', 'None', 'tmp')
      res["vg"] = _vg
      res["ig"] = _ig
      res["vb"] = _vb
      res["ib"] = _ib
      res["wg"] = _wg
      res["wb"] = _wb
      res["ic"] = _ic
      res["tmp"] = _tmp
      res["chksum"] = _chksum
      self.response = res
    elif _cmd == 0x89: #NAK
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
        _vg = 0.0
        _vg = int(eza2500_util.q_normalize(_vg, 14, '380', 'None', 'None', 'vg'))
        _ig = 0.0
        _ig = int(eza2500_util.q_normalize(_ig, 13, '7.8125', 'None', 'None', 'ig'))
        _vb = 0.0
        _vb = int(eza2500_util.q_normalize(_vb, 14, '48', 'None', 'None', 'vb'))
        _ib = 0.0
        _ib = int(eza2500_util.q_normalize(_ib, 13, '52.08', 'None', 'None', 'ib'))
        _wg = 0.0
        _wg = int(eza2500_util.q_normalize(_wg, 11, '2500', 'None', 'None', 'wg'))
        _wb = 0.0
        _wb = int(eza2500_util.q_normalize(_wb, 11, '2500', 'None', 'None', 'wb'))
        _ic = 0
        _tmp = 0.0
        _tmp = int(eza2500_util.q_normalize(_tmp, 7, '1', 'None', 'None', 'tmp'))
        _chksum = 0
        data = pack("<BBBBBhhhhhhhhH", 2, Command1001.ACK_LEN, 1, 2, 0x09, _vg ,_ig ,_vb ,_ib ,_wg ,_wb ,_ic ,_tmp ,_chksum)
        _chksum = eza2500_util.calc_check_sum(data)
        self.reader = StringIO.StringIO(data[:-2] + ('%c%c' % ((_chksum % 256), (_chksum // 256))))
      def read(self, bytes):
        return self.reader.read(bytes)
      def write(self, data):
        essx_debug.dump(data)

    if dev == None:
      dev = Dummy()

    cmd = Command1001(dev)
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
    Command1001.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
