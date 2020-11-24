# -*- coding: utf-8 -*-

import time
from essx.essx_exception import ESSXTimeoutException, ESSXValueException, ESSXChecksumException, ESSXDeviceException
import eza2500
from essx import essx_util
import threading
from essx import essx_debug

class ESSXTypeOES:
    """
    Rest APIとデバイスのやりとりをするコントローラクラス
    """
    def __init__(self, dcdc_dev = None, bat_dev = None, dcdc_config = None, bat_config = None, ad1 = 0, ad2 = 1, name = None):
        self.dcdc_config = dcdc_config
        self.bat_config = bat_config

        self.dcdc_dev = dcdc_dev
        self.bat_dev = bat_dev
        self.ad1 = ad1
        self.ad2 = ad2
        self.name = name

        self.com0101 = eza2500.Command0101(self.dcdc_dev)
        self.com0201 = eza2500.Command0201(self.dcdc_dev)
        self.com0301 = eza2500.Command0301(self.dcdc_dev)
        self.com0304 = eza2500.Command0304(self.dcdc_dev)
        self.com0401 = eza2500.Command0401(self.dcdc_dev)
        self.com0601 = eza2500.Command0601(self.dcdc_dev)
        self.com0701 = eza2500.Command0701(self.dcdc_dev)
        self.com0901 = eza2500.Command0901(self.dcdc_dev)
        self.com1001 = eza2500.Command1001(self.dcdc_dev)

        self.com0104 = eza2500.Command0104(self.dcdc_dev)
        self.com0404 = eza2500.Command0404(self.dcdc_dev)
        self.com0604 = eza2500.Command0604(self.dcdc_dev)
        self.com0704 = eza2500.Command0704(self.dcdc_dev)
        self.com0904 = eza2500.Command0904(self.dcdc_dev)

        self.battery_watchdog_running = True
        self.battery_watchdog_thread = threading.Thread(target = self._battery_watchdog)
        self.battery_watchdog_thread.daemon = True
        self.battery_watchdog_thread.start()


    def vrfy(self, obj, params = {}):
        """
        コマンドのパラメータが正しいかどうかを確認する。
        """
        obj.pack_senddata(self.ad1, self.ad2, params)

    def run(self, obj, params = {}):
        """
        コマンドを送って/受信をする。
        エラーが発生したらリトライをする。
        リトライ回数はEssCommConfigで設定する
        """

        if 'number_of_dcdc_error_retry' in self.dcdc_config:
            retry = int(self.dcdc_config['number_of_dcdc_error_retry'])
        else:
            retry = 0
        if 'number_of_timeout_retry' in self.dcdc_config:
            timeout_retry = int(self.dcdc_config['number_of_timeout_retry'])
        else:
            timeout_retry = 0

        if 'wait_retry' in self.dcdc_config:
            wait_retry = int(self.dcdc_config['wait_retry'])
        else:
            wait_retry = 0.1

        retry += 1
        timeout_retry += 1
        while retry > 0 and timeout_retry > 0:
            try:
                obj.send(self.ad1, self.ad2, params)
                obj.recv()
                time.sleep(0.062)
                return
            except ESSXTimeoutException as err:
                print("timeout retry: " + str(timeout_retry))
                timeout_retry = timeout_retry - 1
                if timeout_retry == 0:
                    raise
                time.sleep(wait_retry)
            except ESSXValueException as err:
                print("value exception    retry: " + str(retry))
                retry = retry - 1
                if retry == 0:
                    raise
                time.sleep(wait_retry)
            except ESSXChecksumException as err:
                print("checksum exception    retry: " + str(retry))
                retry = retry - 1
                if retry == 0:
                    raise
                time.sleep(wait_retry)
            except ESSXDeviceException as err:
                _ercd = obj.response['ercd']
                if _ercd == 0xffff: #受信したコマンドをサポートしていない
                    raise
                elif _ercd == 0xfffe: #コマンドのパラメータが不正
                    raise
                elif _ercd == 0xfffd: #正常だが受付不能
                    pass
                elif _ercd == 0xfffc: #システムビジー
                    pass
                elif _ercd == 0xfffb: #内部通信異常
                    raise
                retry = retry - 1
                if retry == 0:
                    raise ESSXTimeoutException('timeout')
                time.sleep(wait_retry)
        #ここには到達しないはずだが保険
        raise ESSXTimeoutException('timeout')

    def _check_battery(self):
        if self.bat_dev == None:
            return (0, 0, -1)
        else:
            return self.bat_dev.check_battery()
#        rsoc = 0
#        bos = 0
#        comm_err1 = -1
#        comm_err2 = -1
#
#        retry = 2
#        while retry > 0 and self.bat_dev != None:
#            mes = self.bat_dev.read_rsoc()
#            #一分内のデータか？(この値が適切かは考慮するところ)
#            if mes != None and mes.timestamp > time.time() - 60:
#                rsoc = (mes.data[2] + mes.data[3] * 256) / 10.0
#                comm_err1 = 0
#                break
#            else:
#                self.bat_dev.remote_rsoc()
#                time.sleep(0.5)
#                retry = retry - 1
#                rsoc = 0
#
#        retry = 2
#        while retry > 0 and self.bat_dev != None:
#            mes = self.bat_dev.read_status()
#            #一分内のデータか？(この値が適切かは考慮するところ)
#            if mes != None and mes.timestamp > time.time() - 60:
#                if mes.data[0] == 1:
#                    bos = 3
#                else:
#                    bos = 0
#                comm_err2 = 0
#                break
#            else:
#                self.bat_dev.remote_status()
#                time.sleep(0.5)
#                retry = retry - 1
#                bos = 0
#
#        if comm_err1 == 0 and comm_err2 == 0:
#            comm_err = 0
#        else:
#            comm_err = -1
#        return (rsoc, bos, comm_err)

    def _battery_watchdog(self):
        """
        10秒に一回バッテリの融通チェックをする
        """
        essx_debug.log("watchdog start")
        while self.battery_watchdog_running:
            if self.bat_config == None:
                time.sleep(10)
                continue
            essx_debug.log("watchdog")
            essx_debug.log(self.bat_config['config'])
            if 'force_dcdc_waiting' in self.bat_config['config'] and self.bat_config['config']['force_dcdc_waiting'] == True:
                (rsoc, bos, comm_err) = self._check_battery()
                essx_debug.log("rsoc " +str(rsoc))
                essx_debug.log("bos " +str(bos))
                if bos == 0:
                    essx_debug.log("->waiting")
                    self.run(self.com0104, {
                        'mode': self.checkOperationMode_2500(0)
                    })
            time.sleep(10)
        essx_debug.log("watchdog stop")

    # /1/log/data
    def log_data(self, params):
        _dcdc_conf = self.dcdc_config['config']
        _bat_conf = self.bat_config['config']

        (rsoc, bos, comm_err) = self._check_battery()

        if comm_err == -1:
            raise ESSXDeviceException('comm error')
#        if bos == 0:
#            if 'force_dcdc_waiting' in self.bat_config['config'] and self.bat_config['config']['force_dcdc_waiting'] == True:
#                self.run(self.com0104, {
#                        'mode': self.checkOperationMode_2500(0)
#                })

        return {
            "system_time": {
                "year": 0,
                "month": 0,
                "day": 0,
                "hour": 0,
                "minute": 0
            },
            "rsoc": float(rsoc),
            "dischargeable_time": {
                "hour": 0,
                "minute": 0
            },
            "battery_voltage": _bat_conf['battery_voltage'],
            "battery_current": _bat_conf['battery_current'],
            "battery_rsoc" : float(rsoc),
            "battery_status": 0,
            "battery_warning": 0,
            #"battery_alarm": 0
            "battery_operation_status": bos,
            "battery_comm_err": comm_err,
            "charge_discharge_power": _bat_conf['battery_voltage'] * _bat_conf['battery_current'],
            "ups_operation_schedule": 0,
            "ups_operation_mode": {
                "mode": 0,
                "parameter": 0,
                "stop_mode": 0
            },
            #"ups_input_voltage": res["ac_input_voltage"],
            #"ups_output_voltage": res["ac_output_voltage"],
            #"ups_output_current": res["ac_output_current_r"] + res["ac_output_current_s"],
            #"ups_output_frequency": res["ac_output_frequency"],
            #"ups_output_power": res["ac_output_power"],
            #"pvc_charge_voltage": res["pvc_charge_voltage"],
            #"pvc_charge_current": res["pvc_charge_current"],
            #"pvc_charge_power": res["pvc_charge_power"],
            #"pvc_alarm": res["pvc_alarm"],
            #"ups_alarm": res["inverter_alarm"]
        }

    def remote_ioctl_set(self, params):
        _conf = self.dcdc_config['config']
        # EZA2500は 6-4で DIG, CIBを指定する必要がある。CIBは設定より得られるが
        # DIGは設定より得られないので、6-1で今の値を取得する
        self.run(self.com0601)
        self.run(self.com0604, {
                'ubv': _conf['ubv'],
                'ugv': _conf['ugv'],
                'obv': _conf['obv'],
                'ogv': _conf['ogv'],
                'cib': _conf['cib'],
                'dig': self.com0601.response['dig']
        })
        self.run(self.com0704, {
            'bcf': essx_util.strToNum(_conf['bcf']),
            'cvb': _conf['cvb'], #tvb => cvb
            'dlb': _conf['dlb'], #lbv => dlb
            'cdb': _conf['cdb'], #cud => cdb
            'ddb': _conf['ddb'], #dld => ddb
        })
        self.run(self.com0304, {
            'cvb': _conf['cvb'],
            'drb': _conf['drb'],
        })

        res = {}
        res["dcdc_converter_name"] = self.name
        #設定の戻値ではなく設定した値そのものを返す
        res["dcdc_setup_parameter"] = {
            "ubv": _conf['ubv'],
            "ugv": _conf['ugv'],
            "obv": _conf['obv'],
            "ogv": _conf['ogv'],
            "bcf": "0x" + ("%04x" % _conf['bcf']),
            "cvb": _conf['cvb'],
            "dlb": _conf['dlb'],
            "cdb": _conf['cdb'],
            "ddb": _conf['ddb'],
            "drb": _conf['drb'],
            "cib": _conf['cib'],
            #"lbd": _conf['lbd']
        }
        return res

    def remote_ioctl_get(self, params):
        _res_log_data = self.log_data(params)
        _res_remote_get = self.remote_get(params)
        return {
            "status": _res_remote_get["status"],
            "powermeter": _res_remote_get["powermeter"],
            "meter": _res_remote_get["meter"],
            "vdis": _res_remote_get["vdis"],
            "param": _res_remote_get["param"],
            "system_time": _res_log_data["system_time"],
            "rsoc": _res_log_data["rsoc"],
            "dischargeable_time": _res_log_data["dischargeable_time"],
            "battery_voltage": _res_log_data["battery_voltage"],
            "battery_current": _res_log_data["battery_current"],
            "battery_rsoc" : _res_log_data["battery_rsoc"],
            "battery_status": _res_log_data["battery_status"],
            "battery_warning": _res_log_data["battery_warning"],
            #"battery_alarm": 0
            "battery_operation_status": _res_log_data["battery_operation_status"],
            "battery_comm_err": _res_log_data["battery_comm_err"],
            "charge_discharge_power": _res_log_data["charge_discharge_power"],
            "ups_operation_schedule": _res_log_data["ups_operation_schedule"],
            "ups_operation_mode": _res_log_data["ups_operation_mode"],
            #"ups_input_voltage": res["ac_input_voltage"],
            #"ups_output_voltage": res["ac_output_voltage"],
            #"ups_output_current": res["ac_output_current_r"] + res["ac_output_current_s"],
            #"ups_output_frequency": res["ac_output_frequency"],
            #"ups_output_power": res["ac_output_power"],
            #"pvc_charge_voltage": res["pvc_charge_voltage"],
            #"pvc_charge_current": res["pvc_charge_current"],
            #"pvc_charge_power": res["pvc_charge_power"],
            #"pvc_alarm": res["pvc_alarm"],
            #"ups_alarm": res["inverter_alarm"]
        }

    def remote_get(self, params):
        _conf = self.dcdc_config['config']
        self.run(self.com0101, {})
        self.run(self.com0201, {})
        self.run(self.com0401, {})
        self.run(self.com0901, {})
        self.run(self.com1001, {})
        self.run(self.com0601, {})

        res = {}

        res["operationMode"] = self.com0101.response['mode']
        res["alarmState"] = (self.com0201.response['cst'] & 0xc) >> 2
        res["alarm"] = (self.com0901.response['alm1'])
        res["status"] =    (self.com0201.response['cst'] & 0x3)
        res["wg"] = round(self.com1001.response['wg'], 16)
        res["tmp"] = round(self.com1001.response['tmp'],16) 
        res["vb"] = round(self.com1001.response['vb'], 16)
        res["wb"] = round(self.com1001.response['wb'], 16)
        res["vg"] = round(self.com1001.response['vg'], 16)
        res["ib"] = round(self.com1001.response['ib'], 16)
        res["ig"] = round(self.com1001.response['ig'], 16)
        res["dvg"] = round(self.com0401.response['dvg'], 16)  #tgv => dvg
        res["drg"] = round(self.com0401.response['drg'], 16)
        res["dig"] = round(self.com0601.response['dig'], 16) #lgc, lgd => dig


        return {
            "status": {
                "status": "0x" + ('%04x' % res["operationMode"]),
                "alarmState": essx_util.alarmStateStr(res["alarmState"]),
                "statusName": "Ignore",
                "alarm": essx_util.alarmStr(res["status"], res["alarmState"], res["alarm"]),
                "runningState": essx_util.runningStateStr(res['status']),
                "operationMode": essx_util.operationModeStr(res["operationMode"]),
            },
            "powermeter": {
                "p2": 0,
                "p1": 0,
                "v1": 0,
                "kwh2": 0,
                "kwh1": 0,
                "i1": 0
            },
            "meter": {
                "wg": res["wg"],
                "tmp": res["tmp"],
                "vb": res["vb"],
                "wb": res["wb"],
                "vg": res["vg"],
                "ib": res["ib"],
                "ig": res["ig"]
            },
            "vdis": {
                "dvg": res["dvg"],
                "drg": res["drg"]
            },
            "param": {
                'cib': _conf['cib'],
                'ubv': _conf['ubv'],
                "dig": res["dig"],
                'ogv': _conf['ogv'],
                'obv': _conf['obv'],
                'ugv': _conf['ugv'],
            }
        }

    def remote_get_status(self, params):
        self.run(self.com0101)
        self.run(self.com0201)
        self.run(self.com1001)

        res = {}
        res["operationMode"] = self.com0101.response['mode']
        res["alarmState"] = (self.com0201.response['cst'] & 0xc) >> 2
        res["status"] =    (self.com0201.response['cst'] & 0x3)
        res["wg"] = round(self.com1001.response['wg'], 16)
        res["tmp"] = round(self.com1001.response['tmp'], 16)
        res["vb"] = round(self.com1001.response['vb'], 16)
        res["wb"] = round(self.com1001.response['wb'], 16)
        res["vg"] = round(self.com1001.response['vg'], 16)
        res["ib"] = round(self.com1001.response['ib'], 16)
        res["ig"] = round(self.com1001.response['ig'], 16)


        return {
            "status": {
                "alarmState": essx_util.alarmStateStr(res["alarmState"]),
                "runningState": essx_util.runningStateStr(res['status']),
                "operationMode": essx_util.operationModeStr(res["operationMode"]),
            },
            "meter": {
                "wg": res["wg"],
                "tmp": res["tmp"],
                "vb": res["vb"],
                "wb": res["wb"],
                "vg": res["vg"],
                "ib": res["ib"],
                "ig": res["ig"]
            },
        }

    def remote_set(self, params):
        """
        以下のパラメータが必要である
        params['mode']
        params['dvg']
        params['drg']
        params['dig']

        'mode'は16進数の文字列(EZA2500値)で指定する。
        読み変えはしない
        """
        _conf = self.dcdc_config['config']

        _local_current_mode = params['current_mode'] ##############Added for v1.3 2018/11/14##################

        self.vrfy(self.com0404, {
            'dvg': params['dvg'], 'drg': params['drg']
        })

        self.vrfy(self.com0604, {
            'ubv': _conf['ubv'],
            'ugv': _conf['ugv'],
            'obv': _conf['obv'],
            'ogv': _conf['ogv'],
            'cib': _conf['cib'],
            'dig': params['dig'],
        })
        self.vrfy(self.com0104, {
            'mode': self.checkOperationMode_2500(essx_util.hexStrToInt(params['mode']))
        })

        #############Added for v1.3 2018/11/14 現在のModeによってコマンドの発行順を変える。###################
        ##########################################↓↓↓#########################################################
        if _local_current_mode  == '0x0000':
             self.run(self.com0404, {
                 'dvg': params['dvg'], 'drg': params['drg']
             })
             self.run(self.com0604, {
                 'ubv': _conf['ubv'],
                 'ugv': _conf['ugv'],
                 'obv': _conf['obv'],
                 'ogv': _conf['ogv'],
                 'cib': _conf['cib'],
                 'dig': params['dig'],
             })
             self.run(self.com0104, {
                 'mode': self.checkOperationMode_2500(essx_util.hexStrToInt(params['mode']))
             })
        else:
             self.run(self.com0104, {
                 'mode': self.checkOperationMode_2500(essx_util.hexStrToInt(params['mode']))
             })
             self.run(self.com0404, {
                 'dvg': params['dvg'], 'drg': params['drg']
             })
             self.run(self.com0604, {
                 'ubv': _conf['ubv'],
                 'ugv': _conf['ugv'],
                 'obv': _conf['obv'],
                 'ogv': _conf['ogv'],
                 'cib': _conf['cib'],
                 'dig': params['dig'],
             })
        ##########################################↑↑↑######################################################
        ###################################################################################################
        
        self.run(self.com0201)
        self.run(self.com0901)
        self.run(self.com1001)

        res = {}
        res["operationMode"] = self.com0104.response['mode']
        res["alarmState"] = (self.com0201.response['cst'] & 0xc) >> 2
        res["alarm"] = (self.com0901.response['alm1'])
        res["status"] = (self.com0201.response['cst'] & 0x3)
        res["wg"] = round(self.com1001.response['wg'], 16)
        res["tmp"] = round(self.com1001.response['tmp'], 16)
        res["vb"] = round(self.com1001.response['vb'], 16)
        res["wb"] = round(self.com1001.response['wb'], 16)
        res["vg"] = round(self.com1001.response['vg'], 16)
        res["ib"] = round(self.com1001.response['ib'], 16)
        res["ig"] = round(self.com1001.response['ig'], 16)
        res["dvg"] = round(self.com0404.response['dvg'], 16)
        res["drg"] = round(self.com0404.response['drg'], 16)
        res["dig"] = round(self.com0604.response['dig'], 16)

        return {
            "status": {
                "status": "0x" + ('%04x' % res["operationMode"]),
                "alarmState": essx_util.alarmStateStr(res["alarmState"]),
                "statusName": "Ignore",
                "alarm": essx_util.alarmStr(res["status"], res["alarmState"], res["alarm"]),
                "runningState": essx_util.runningStateStr(res['status']),
                "operationMode": essx_util.operationModeStr(res["operationMode"]),
            },
            "meter": {
                "wg": res["wg"],
                "tmp": res["tmp"],
                "vb": res["vb"],
                "wb": res["wb"],
                "vg": res["vg"],
                "ib": res["ib"],
                "ig": res["ig"]
            },
            "vdis": {
                "dvg": res["dvg"],
                "drg": res["drg"]
            },
            "param": {
                'cib': _conf['cib'],
                'ubv': _conf['ubv'],
                "dig": res["dig"],
                'ogv': _conf['ogv'],
                'obv': _conf['obv'],
                'ugv': _conf['ugv'],
            }
        }

    def remote_set_current(self, params):
        """
        digが必須
        mode, dvg, drg も上層より指定されてくるが必須ではない。
        """
        _conf = self.dcdc_config['config']

        self.vrfy(self.com0604, {
            'ubv': _conf['ubv'],
            'ugv': _conf['ugv'],
            'obv': _conf['obv'],
            'ogv': _conf['ogv'],
            'cib': _conf['cib'],
            'dig': params['dig'],
        })

        self.run(self.com0604, {
            'ubv': _conf['ubv'],
            'ugv': _conf['ugv'],
            'obv': _conf['obv'],
            'ogv': _conf['ogv'],
            'cib': _conf['cib'],
            'dig': params['dig'],
        })
        self.run(self.com1001)
        res = {}
        res["wg"] = round(self.com1001.response['wg'], 16)
        res["tmp"] = round(self.com1001.response['tmp'], 16)
        res["vb"] = round(self.com1001.response['vb'], 16)
        res["wb"] = round(self.com1001.response['wb'], 16)
        res["vg"] = round(self.com1001.response['vg'], 16)
        res["ib"] = round(self.com1001.response['ib'], 16)
        res["ig"] = round(self.com1001.response['ig'], 16)
        res["dig"] = round(self.com0604.response['dig'], 16)

        return {
            "meter": {
                "wg": res["wg"],
                "tmp": res["tmp"],
                "vb": res["vb"],
                "wb": res["wb"],
                "vg": res["vg"],
                "ib": res["ib"],
                "ig": res["ig"]
            },
            "param": {
                'cib': _conf['cib'],
                'ubv': _conf['ubv'],
                "dig": res["dig"],
                'ogv': _conf['ogv'],
                'obv': _conf['obv'],
                'ugv': _conf['ugv'],
            }
        }


    def remote_set_voltage(self, params):
        """
        dvg, drg が必須
        mode, digも上層より指定されてくるが必須ではない。
        """
        self.vrfy(self.com0404, {
            'dvg': params['dvg'], 'drg': params['drg']
        })
        self.run(self.com0404, {
            'dvg': params['dvg'], 'drg': params['drg']
        })

        self.run(self.com1001)
        res = {}
        res["wg"] = round(self.com1001.response['wg'], 16)
        res["tmp"] = round(self.com1001.response['tmp'], 16)
        res["vb"] = round(self.com1001.response['vb'], 16)
        res["wb"] = round(self.com1001.response['wb'], 16)
        res["vg"] = round(self.com1001.response['vg'], 16)
        res["ib"] = round(self.com1001.response['ib'], 16)
        res["ig"] = round(self.com1001.response['ig'], 16)
        res["dvg"] = round(self.com0404.response['dvg'], 16)
        res["drg"] = round(self.com0404.response['drg'], 16)

        return {
            "meter": {
                "wg": res["wg"],
                "tmp": res["tmp"],
                "vb": res["vb"],
                "wb": res["wb"],
                "vg": res["vg"],
                "ib": res["ib"],
                "ig": res["ig"]
            },
            "vdis": {
                "dvg": res["dvg"],
                "drg": res["drg"]
            },
        }

    def remote_ioctl_clr_alarm(self, params):
        self.run(self.com0904, {
            'd0': 0, 'd1': 0,
        })
        return self.remote_get(params)

    def checkOperationMode_2500(self, v):
        """
        EZA2500のoperationModeの確認
        """
        if v == 0x0:
            return v
        elif v == 0x2:
            return v
        elif v == 0x14:
            return v
        elif v == 0x41:
            return v
        raise ESSXValueException("bad value: operation mode: " + str(v))

if __name__    == "__main__":
    #単体テストのためにはデバイスの先に装置(esscomm/ess2/test.py で代用可)が必要
    import serial
    import traceback
    import essx

    ser_dev = essx.essx_rs232c.ESSXRS232C("/dev/cuaU1", 19200)
    dcdc_dev = eza2500.EZA2500Device(dev = ser_dev, timeout = 1)
    controller = ESSXType3(dcdc_dev = dcdc_dev, bat_dev = None, dcdc_config = {
        'config': {
            'bcf': 0,
#            'lbc': 45.8, #バッテリ上限電流(充電)
#            'lbd': 45.8, #バッテリ上限電流(放電)
            'ubv': 60,  #バッテリ低電圧閾値
            'obv': 60,  #バッテリ過電圧閾値
            #'lgc': 34.4, #グリッド上限電流(充電)
            #'lgd': 34.4, #グリッド上限電流(放電)
            'ugv': 280,  #グリッド低電圧閾値
            'ogv': 280,  #グリッド過電圧閾値
            #'tgv': 240,  #グリッド目標電圧
            'cvb': 40,  #バッテリ目標電圧
            'dlb': 40,  #バッテリ放電終止電圧
            'cdb': 6,   #バッテリ充電上限予告電圧偏差
            'ddb': 6,   #バッテリ充電終止予告電圧偏差
            #'drg': 0.25, #グリッドドループ率
            'drb': 0.25, #バッテリドループ率
            'cib': 45.8,
        }}, bat_config = {
            'config': {
                'battery_voltage': 200,
                'battery_current': 2.0
            }}
    )

    try:
        print("/1/log/data")
        print(controller.log_data({}))
        print("remote/ioctl/get")
        print(controller.remote_ioctl_get({}))
        print("remote/ioctl/set")
        print(controller.remote_ioctl_set({}))
        print(controller.remote_get({}))
        print(controller.remote_get_status({}))
        print(controller.remote_set({'mode': '0x02', 'dvg': 300, 'drg': 0.1, 'dig': 0}))
        print(controller.remote_set_current({'dig': 3}))
        print(controller.remote_set_voltage({'dvg': 360, 'drg': 0.2}))
        print(controller.remote_ioctl_clr_alarm({}))
    except ESSXValueException as err:
        print(err.reason)
        print(traceback.format_exc())
        raise err
