# -*- coding: utf-8 -*-
#!/usr/bin/env python
# for bbb84
import sys
try:
    from essx import essx_rs485 #BBB以外でも動くように
except ImportError as err:
    sys.stderr.write("warning: cannot import essx_rs485\n")

import serial
import copy
from pymodbus.client.sync import ModbusSerialClient #, ModbusTcpClient

#class ESSXModbusTcpClient(ModbusTcpClient):
#    pass

class ESSXModbusClient(ModbusSerialClient):
    """
    pymodbusのSerialClientは直接内部で serial.Serialを生成し使用している。
    これは直書きされており別のクラスに変更することはできないようだ。
    このプロジェクトでは serial.Serialを継承したクラスを利用しているので
    のでそれを置き換えるクラス
    """
    def __init__(self, *args, **kwargs):
        if 'dir_pin' in kwargs:
            self.dir_pin = kwargs['dir_pin']
            kwargs = copy.copy(kwargs)
            del kwargs['dir_pin']
        else:
            self.dir_pin = "P8_9"

        print("dir_pin: {}".format(self.dir_pin))

        super(ESSXModbusClient, self).__init__(*args, **kwargs)

    def connect(self):
        """ Connect to the modbus serial server
        :returns: True if connection succeeded, False otherwise
        """
        if self.socket:
            return True
        try:
            self.socket = essx_rs485.ESSXRS485(
                port = self.port,
                timeout = self.timeout,
                bytesize = self.bytesize,
                stopbits = self.stopbits,
                baudrate = self.baudrate,
                parity = self.parity,
                dir_pin = self.dir_pin
            )
        except serial.SerialException as msg:
            print(msg)
            self.close()
        if self.method == "rtu":
            self.last_frame_end = None
        return self.socket is not None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default = "/dev/ttyO4")
    parser.add_argument('--speed', default = 9600, type = int)
    parser.add_argument('--unit', default = 1, type = int)
    args = parser.parse_args()
    print("device={}".format(args.device))
    print("speed={}".format(args.speed))
    print("unit={}".format(args.unit))

    # client = ModbusClient('192.168.252.96', port=5020)
    # from pymodbus.transaction import ModbusRtuFramer
    # client = ModbusClient('localhost', port=5020, framer=ModbusRtuFramer)
    # client = ModbusClient(method='binary', port='/dev/ptyp0', timeout=1)
    # client = ModbusClient(method='ascii', port='/dev/ptyp0', timeout=1)
    client = ESSXModbusClient(method='rtu', port=args.device, timeout=1,
                              baudrate=args.speed, dir_pin="P8_7")
    client.connect()

    rr = client.read_input_registers(0, 31, unit=args.unit)
    print(rr.__class__)
    print(rr.getRegister(30001 - 30001) == 0x3031) #protocol version
    print(rr.getRegister(30002 - 30001) == 0x3030) #protocol version
    print(rr.getRegister(30003 - 30001) == 0x3030) #protocol version
    print(rr.getRegister(30010 - 30001) == ord("H")*256 + ord("E")) #vendor name
    print("rsoc={}".format(rr.getRegister(30030 - 30001) / 10.0))
    print("status={}".format(rr.getRegister(30031 - 30001)))
    rr = client.read_input_registers(30030 - 30001, 2, unit=args.unit)
    print(rr.__class__)
    print("rsoc={}".format(rr.getRegister(0) / 10.0))
    print("status={}".format(rr.getRegister(1)))

    # ----------------------------------------------------------------------- #
    # close the client
    # ----------------------------------------------------------------------- #
    client.close()

