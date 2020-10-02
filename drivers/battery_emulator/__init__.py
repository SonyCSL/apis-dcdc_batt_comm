# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import time
import pymodbus
from essx.essx_exception import ESSXDeviceException

# RSOC等を取りにいく間隔。この時間経過しないとmodbusコマンドを発行しない
# 0にすると必ず発行する
T = 0
class BatteryEmulator(object):
    def __init__(self, dev = None, modbus_adr_rsoc = None, modbus_adr_status = None, unit = 0x1):
        """
        :param pymodbus.client.sync.ModbusSerialCliet dev: デバイス
        :param int modbus_adr_rsoc: RSOCのアドレス
        :param int modbus_adr_status: STATUSのアドレス
        :param int unit: UNIT
        """
        self.dev = dev #
        self.modbus_adr_rsoc = modbus_adr_rsoc
        self.modbus_adr_status = modbus_adr_status
        self.unit = unit
        self._rsoc = 0.0
        self._status = 1
        self._rsoc_ts = 0
        self._status_ts = 0

    def read_rsoc(self):
        """
        rsocを取得する

        :return RSOC: 0 - 100.0
        :rtype float:

        事前に remote_rsocが実行されている必要がある
        """
        return self._rsoc / 10.0

    def read_status(self):
        """
        statusを取得する

        :return 融通可 1 / 融通不可 0
        :rtype int:

        要求仕様書では modbusの該当レジスタが0のときに融通可, 1のときに不可と
        意味合いが逆であることに注意。

        事前に read_statusが実行されている必要がある
        """
        return 0 if (self._status & 0x1) == 1 else 1

    def remote_rsoc_and_status(self):
        """ rsocと statusのアドレスが隣りあってるときは一回で取得する """
        if self._rsoc_ts > time.time() - T and self._status_ts > time.time() - T:
            return
        rr = self.dev.read_input_registers(self.modbus_adr_rsoc, 2, unit = self.unit)
        if isinstance(rr, pymodbus.exceptions.ModbusIOException):
            raise ESSXDeviceException("modbus io exception")
        self._rsoc = rr.getRegister(0)
        self._status = rr.getRegister(1)
        self._rsoc_ts = time.time()
        self._status_ts = time.time()

    def remote_rsoc(self):
        """ rsocを取得するコマンドを発行する """
        if self.modbus_adr_status - self.modbus_adr_rsoc == 1:
            self.remote_rsoc_and_status()
            return

        if self._rsoc_ts > time.time() - T:
            return
        rr = self.dev.read_input_registers(self.modbus_adr_rsoc, 1, unit = self.unit)
        if isinstance(rr, pymodbus.exceptions.ModbusIOException):
            raise ESSXDeviceException("modbus io exception")
        self._rsoc = rr.getRegister(0)
        self._rsoc_ts = time.time()


    def remote_status(self):
        """ statusを取得するコマンドを発行する """
        if self._status_ts > time.time() - T:
            return
        rr = self.dev.read_input_registers(self.modbus_adr_status, 1, unit = self.unit)
        if isinstance(rr, pymodbus.exceptions.ModbusIOException):
            raise ESSXDeviceException("modbus io exception")
        self._status = rr.getRegister(0)
        self._status_ts = time.time()

    def check_battery(self):
        """
        :return: (rsoc, bos, commerr)からなるタプル
        :rtype tuple:

        rsocは 0.0から 100.0までの float
        bosは 融通不可: 0, 充電のみ許可: 1, 放電のみ許可: 2, 融通許可: 3
        cmmerrは 通信エラーが発生したか(True)否か(False)
        0と3しか返さない。
        """
        rsoc = 0
        bos = 0
        comm_err1 = -1
        comm_err2 = -1

        retry = 2
        while retry > 0:
            try:
                self.remote_rsoc()
                rsoc = self.read_rsoc()
                comm_err1 = 0
                break
            except pymodbus.exceptions.ModbusIOException:
                time.sleep(0.5)
                retry = retry - 1
                rsoc = 0

        retry = 2
        while retry > 0:
            try:
                self.remote_status()
                bos = 0 if self.read_status() == 0 else 3
                comm_err2 = 0
                break
            except pymodbus.exceptions.ModbusIOException:
                time.sleep(0.5)
                retry = retry - 1
                bos = 0

        if comm_err1 == 0 and comm_err2 == 0:
            comm_err = 0
        else:
            comm_err = -1
        return (rsoc, bos, comm_err)

#単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
if __name__  == "__main__":
    from pymodbus.client.sync import ModbusSerialClient as ModbusClient
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default = "/dev/ttyO4")
    parser.add_argument('--speed', default = 9600, type = int)
    parser.add_argument('--unit', default = 1, type = int)
    args = parser.parse_args()
    print("device={}".format(args.device))
    print("speed={}".format(args.speed))
    print("unit={}".format(args.unit))

    client = ModbusClient(method='rtu', port=args.device, timeout=1, baudrate=args.speed)
    client.connect()
    emubat = BatteryEmulator(dev = client, modbus_adr_rsoc = 0x1d, modbus_adr_status = 0x1e, unit = args.unit)

    emubat.remote_rsoc()
    mes = emubat.read_rsoc()
    if mes != None:
        print("rsoc={}".format(mes))
    time.sleep(0.1)

    emubat.remote_status()
    mes = emubat.read_status()
    if mes != None:
        print("status={}".format(mes))
    time.sleep(0.1)

    print(emubat.check_battery())
