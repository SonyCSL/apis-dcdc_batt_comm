#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#
# リクエストパラメータを覚えておくキャッシュは
# 仕様書にある通りsetで指定されたときのみに
# そのパラメータを保存するように変更した
#

import sys
import os
import bottle
from bottle import route, HTTPResponse
import argparse
import serial
import essx
from essx.essx_exception import ESSXException, ESSXConfigException, ESSXParameterException
from essx.essx_modbus import ESSXModbusClient
from essx.essx_rs485 import ESSXRS485
import yaml

parser = argparse.ArgumentParser(description = 'ESS Server')
parser.add_argument('--host', default = "localhost")
parser.add_argument('--port', default = 8080, type = int)
parser.add_argument('--debug', action = 'store_true')
parser.add_argument('--goodbye', action = 'store_true')
parser.add_argument('--config', default = "dcdc_batt_comm.yml")
args = parser.parse_args()

if args.debug == True:
  os.environ['ESSX_LOG_LEVEL'] = '7'

class ESSXConfig(object):
  """
  設定ファイルを管理するクラス。このクラスはSingletonである。
  """
  _instance = None

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super(ESSXConfig, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__(self, config_file):
    self.config_file = config_file
    self.reload()

  def reload(self):
    f = open(self.config_file)
    self._config = yaml.load(f)
    f.close()

  def config(self):
    return self._config

  def __getitem__(self, i):
    return self._config[i]

def init_controller(dcdc_unit = 0, battery_unit = 0):
  """
  controllerを設定ファイルに従って初期化して得る。

  @param dcdc_unit DCDC unit number
  @param battery_unit Battery unit number
  """
  ess_system_config = app_config['ess_system']

  if ess_system_config['type'] == 'essx_type_oes':
    import essx.essx_type_oes
    import eza2500
    import battery_emulator

    dcdc_config = ess_system_config['dcdc_dev'][dcdc_unit]
    bat_config = ess_system_config['battery_dev'][battery_unit]

    if dcdc_config['class'] == 'ESSXRS485':
      dcdc_dev_params = dcdc_config['params']
      dcdc_dev_kwparams = dcdc_config['kwparams']
      ser_dev = essx.essx_rs485.ESSXRS485(*dcdc_dev_params, **dcdc_dev_kwparams)
      dcdc_dev = eza2500.EZA2500Device(dev = ser_dev, timeout = 0.1)
    else:
      raise ESSXConfigException('dcdc_config')

    if bat_config['class'] == 'ESSXModbus':
      bat_dev_params = bat_config.get('params', [])
      if 'kwparams' in bat_config:
        bat_dev_kwparams = bat_config['kwparams']
      else:
        bat_dev_kwparams = {}
      dev = essx.essx_modbus.ESSXModbusClient(*bat_dev_params, **bat_dev_kwparams)
      bat_dev = battery_emulator.BatteryEmulator(dev = dev, modbus_adr_rsoc = bat_config['modbus_adr_rsoc'] - 30001, modbus_adr_status = bat_config['modbus_adr_status'] - 30001, unit = bat_config['unit'])
    elif bat_config['class'] == 'None':
      bat_dev = None
    else:
      raise ESSXConfigException('bat_config')

    dcdc_config_name = dcdc_config['config']
    bat_config_name = bat_config['config']
    controller = essx.essx_type_oes.ESSXTypeOES(
      dcdc_dev = dcdc_dev,
      bat_dev = bat_dev,
      dcdc_config = app_config['dcdc'][dcdc_config_name],
      bat_config = app_config['battery'][bat_config_name],
      ad1 = int(dcdc_config['address1']),
      ad2 = int(dcdc_config['address2']),
      name = dcdc_config['name'],
    )
  else:
      print("unknown controller: " + ess_system_config['type'])
      sys.exit(0)

  return controller

def essx_exception_handler(func):
  """ essx_exceptionが発生したときの例外デコレーター """
  import functools
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      res = func(*args, **kwargs)
      return res
    except ESSXException as err:
      body = {'err': err.reason}
      res = HTTPResponse(status=400, body=body)
      res.set_header('Content-Type', 'application/json')
      return res
    except Exception as err:
      body = {'err': str(err)}
      res = HTTPResponse(status=400, body=body)
      res.set_header('Content-Type', 'application/json')
      return res

  return wrapper

@route('/essx/hello')
@essx_exception_handler
def hello():
  """ デバッグ用 """
  body = {'message': 'hello world'}
  r = HTTPResponse(status=200, body=body)
  r.set_header('Content-Type', 'application/json')
  essx.ESSXGlobal.reset(0)
  return r

@route('/essx/goodbye')
@essx_exception_handler
def goodbye():
  """ デバッグ用 """
  if args.goodbye:
      body = {'message': 'goodbye'}
      r = HTTPResponse(status=200, body=body)
      r.set_header('Content-Type', 'application/json')
      essx.ESSXGlobal.reset(0)
      print("GOODBYE!")
      os._exit(0)

@route('/battery/get')
@route('/1/log/data')
@essx_exception_handler
def cmd_get_1_log_data():
  res = controller.log_data({})
  if bottle.request.fullpath == '/battery/get':
      res = {'rsoc': res['rsoc'], 'battery_operation_status': res['battery_operation_status']}
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

@route('/dcdc/get')
@route('/remote/get')
@essx_exception_handler
def cmd_get_remote_get():
  res = controller.remote_get({})
  if bottle.request.fullpath == '/dcdc/get':
      del res['powermeter']
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

@route('/dcdc/get/status')
@route('/remote/get/status')
@essx_exception_handler
def cmd_get_remote_get_status():
  res = controller.remote_get_status({})
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

_global_current_mode = '0x0000'                           #############Added for v1.3 2018/11/14##########################


@route('/dcdc/set')
@route('/remote/set')
@essx_exception_handler
def cmd_get_remote_set():
  # mode, dvg, dig がパラメータとして必須
  # 省略された場合は cache値から取得。
  # drgの指定がない場合はcache値を取得。キャッシュもない場合は0となる
  params = {}
  req_params = bottle.request.params

  if bottle.request.fullpath == '/dcdc/set':
      # v1.2で /remote/set, /remote/voltage, /remote/currentと同等のAPI
      # /dcdc/setが追加されたが、この3種のAPIは返すJSONデータが微妙に違うので
      # /dcdc/setで digだけのときは /remote/set/currentとみなし、
      # /dcdc/setで dvgだけ、または dvg、drgが設定されているだけのときは /remote/set/voltageとみなす
      # コードを入れる
      if 'dig' in req_params and not 'dvg' in req_params and not 'drg' in req_params and not 'mode' in req_params:
          return cmd_remote_set_current()
      if not 'dig' in req_params and 'dvg' in req_params and not 'mode' in req_params:
          return cmd_remote_set_voltage()

  if 'mode' in req_params:
    params['mode'] = req_params['mode']
  elif essx.ESSXGlobal.has(0, 'mode'):
    params['mode'] = essx.ESSXGlobal.get(0, 'mode')
  else:
    raise ESSXParameterException("No operationMode")

  if 'dig' in req_params:
    params['dig'] = req_params['dig']
  elif essx.ESSXGlobal.has(0, 'dig'):
    params['dig'] = essx.ESSXGlobal.get(0, 'dig')
  else:
    raise ESSXParameterException("No dig")

  if 'dvg' in req_params:
    params['dvg'] = req_params['dvg']
  elif essx.ESSXGlobal.has(0, 'dvg'):
    params['dvg'] = essx.ESSXGlobal.get(0, 'dvg')
  else:
    raise ESSXParameterException("No dvg")

  if 'drg' in req_params:
    params['drg'] = req_params['drg']
  elif essx.ESSXGlobal.has(0, 'drg'):
    params['drg'] = essx.ESSXGlobal.get(0, 'drg')
  else:
    params['drg'] = 0

  global _global_current_mode                             #############Added for v1.3 2018/11/14########################### 
  params['current_mode'] = _global_current_mode           #############Added for v1.3 2018/11/14########################### 

  res = controller.remote_set(params)
 
  _global_current_mode = res['status']['operationMode']   #############Added for v1.3 2018/11/14###########################

  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  essx.ESSXGlobal.put(0, 'mode', params['mode'])
  essx.ESSXGlobal.put(0, 'dig', params['dig'])
  essx.ESSXGlobal.put(0, 'dvg', params['dvg'])
  essx.ESSXGlobal.put(0, 'drg', params['drg'])

  return r

@route('/remote/set/current')
@essx_exception_handler
def cmd_remote_set_current():
  params = {}
  req_params = bottle.request.params

  # modeは下層で必須だが指定はできない
  if essx.ESSXGlobal.has(0, 'mode'):
    params['mode'] = essx.ESSXGlobal.get(0, 'mode')
  else:
    raise ESSXParameterException("No operationMode")

  # digは必須である(仕様書の読み方では無くてもよいようにも取れるが)
  if 'dig' in req_params:
    params['dig'] = req_params['dig']
#  elif essx.ESSXGlobal.has(0, 'dig'):
#    params['dig'] = essx.ESSXGlobal.get(0, 'dig')
  else:
    raise ESSXParameterException("No dig")

  # dvgは下層で必須だが指定はできない
  if essx.ESSXGlobal.has(0, 'dvg'):
    params['dvg'] = essx.ESSXGlobal.get(0, 'dvg')
  else:
    raise ESSXParameterException("No dvg")

  # drgは下層で必要だが指定はできない
  if essx.ESSXGlobal.has(0, 'drg'):
    params['drg'] = essx.ESSXGlobal.get(0, 'drg')
  else:
    params['drg'] = 0

  res = controller.remote_set_current(params)
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  essx.ESSXGlobal.put(0, 'dig', params['dig'])

  return r

@route('/remote/set/voltage')
@essx_exception_handler
def cmd_remote_set_voltage():
  params = {}
  req_params = bottle.request.params

  # modeは下層で必要だが指定はできない
  if essx.ESSXGlobal.has(0, 'mode'):
    params['mode'] = essx.ESSXGlobal.get(0, 'mode')
  else:
    raise ESSXParameterException("No operationMode")

  # digは下層で必要だが指定はできない
  if essx.ESSXGlobal.has(0, 'dig'):
    params['dig'] = essx.ESSXGlobal.get(0, 'dig')
  else:
    raise ESSXParameterException("No dig")

  # dvgは必須である(仕様書の読み方では無くてもよいようにも取れるが)
  if 'dvg' in req_params:
    params['dvg'] = req_params['dvg']
#  elif essx.ESSXGlobal.has(0, 'dvg'):
#    params['dvg'] = essx.ESSXGlobal.get(0, 'dvg')
  else:
    raise ESSXParameterException("No dvg")

  # drgは下層で必要。無い場合は0になる。
  if 'drg' in req_params:
    params['drg'] = req_params['drg']
  elif essx.ESSXGlobal.has(0, 'drg'):
    params['drg'] = essx.ESSXGlobal.get(0, 'drg')
  else:
    params['drg'] = 0

  res = controller.remote_set_voltage(params)
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  essx.ESSXGlobal.put(0, 'dvg', params['dvg'])
  essx.ESSXGlobal.put(0, 'drg', params['drg'])

  return r

@route('/remote/ioctl/set')
@essx_exception_handler
def cmd_remote_ioctl_set():
  app_config.reload()

  dcdc_unit =0
  battery_unit = 0

  ess_system_config = app_config['ess_system']
  dcdc_config = ess_system_config['dcdc_dev'][dcdc_unit]
  bat_config = ess_system_config['battery_dev'][battery_unit]
  dcdc_config_name = dcdc_config['config']
  bat_config_name = bat_config['config']

  controller.dcdc_config = app_config['dcdc'][dcdc_config_name]
  controller.bat_config = app_config['battery'][bat_config_name]

  params = {}
  res = controller.remote_ioctl_set(params)
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

@route('/all/get')
@route('/remote/ioctl/get')
@essx_exception_handler
def cmd_remote_ioctl_get():
  params = {}
  res = controller.remote_ioctl_get(params)
  if bottle.request.fullpath == '/all/get':
      res = {
          'rsoc': res['rsoc'],
          'battery_operation_status': res['battery_operation_status'],
          'meter': res['meter'],
          'param': res['param'],
          'status': res['status'],
          'vdis': res['vdis']
      }
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

@route('/remote/ioctl/clr_alarm')
@essx_exception_handler
def cmd_remote_ioctl_clr_alarm():
  params = {}
  res = controller.remote_ioctl_clr_alarm(params)
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

@route('/version/get')
@essx_exception_handler
def cmd_version_get():
  res = {
      "comm_interface_version": "2.0",
      "dcdc_batt_comm_version": "1.4"
  }
  r = HTTPResponse(status=200, body = res)
  r.set_header('Content-Type', 'application/json')

  return r

app_config = ESSXConfig(args.config)
controller = init_controller()

bottle.run(host = "0.0.0.0", port = args.port, debug = args.debug)
