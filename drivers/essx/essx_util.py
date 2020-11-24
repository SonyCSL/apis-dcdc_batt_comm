# -*- coding: utf-8 -*-

from essx.essx_exception import ESSXValueException
def alarmStateStr(v):
  """
  alarmStateの文字列を得る
  @param v データ
  @return 文字列
  """

  if v == 0:
    return "No alarm"
  elif v == 1:
    return "Light alarm"
  elif v == 2:
    return "Heavy alarm"
  else:
    raise ESSXValueException("bad value: alarmState: " + str(v))

def runningStateStr(v):
  """
  runningStateの文字列を得る

  @param v データ
  @return 文字列
  """
  if v == 0:
      return "off"
  elif v == 1:
      return "charge"
  elif v == 2:
      return "discharge"
  else:
      raise ESSXValueException("bad value: runningState: " + str(v))

def alarmStr(v1, v2, v3):
  """
  alarmの文字列を得る

  @param v データ
  @return 文字列
  """
  return ('%04x' % v3) + " " + ('%04x' % v2) + " " + ('%04x' % v1)

def operationModeStr(v):
  """
  operationModeの文字列を得る

  @param v データ(EZA2500での値を渡す)
  @return 文字列
  """

  if v == 0x0:
    return "Waiting"
  elif v == 0x1:
    return "Hateronomy CV Charging"
  elif v == 0x2: #EZA2500 0x2
    return "Heteronomy CV"
  elif v == 0x22:
    return "Heteronomy CV"
  elif v == 0x4:
    return "Battery Autonomy"
  elif v == 0x14: #EZA2500 0x14
    return "Grid Autonomy"
  elif v == 0x34:
    return "Grid Autonomy CC Battery"
  elif v == 0x41: #EZA2500 0x41
    return "Heteronomy CV"

  raise ESSXValueException("bad value: operationMode: " + str(v))

def hexStrToInt(s):
  """
  0xで始まるhex値の文字列をintにする
  """
  if s[0:2] != '0x':
    raise ESSXValueException("bad value: " + s)

  try:
    return int(s[2:], 16)
  except ValueError as err:
    raise ESSXValueException("bad value: " + s)

def strToNum(s):
  """
  文字列や数字をint(または float)にする

  もしintや float ならそのまま返す
  0xで始まる文字列なら16進と判断してintにする。
  0xで始まらなければ10進と判断する
  """
  if isinstance(s, int):
    return s
  elif isinstance(s, float):
    return s
  elif s[0:2] == '0x':
    try:
      return int(s[2:], 16)
    except ValueError as err:
      raise ESSXValueException("bad value: " + s)
  else:
    try:
      return int(s, 10)
    except ValueError as err:
      raise ESSXValueException("bad value: " + s)

if __name__  == "__main__":
  assert alarmStateStr(0) == 'No alarm'
  assert alarmStateStr(1) == 'Light alarm'
  assert alarmStateStr(2) == 'Heavy alarm'

  assert runningStateStr(0) == 'off'
  assert runningStateStr(1) == 'charge'
  assert runningStateStr(2) == 'discharge'

  assert alarmStr(0, 0, 0) == '0000 0000 0000'
  assert alarmStr(10, 20, 30) == '001e 0014 000a'

  assert operationModeStr(0x00) == "Waiting"
  assert operationModeStr(0x2) == "Heteronomy CV"
  assert operationModeStr(0x14) == "Grid Autonomy"
  assert operationModeStr(0x41) == "Heteronomy CV"

  assert hexStrToInt("0xDEF") == 0xdef
  assert hexStrToInt("0xdef") == 0xdef
  try:
    hexStrToInt("def")
    assert False
  except ESSXValueException as err:
    pass

  assert strToNum(1) == 1
  assert strToNum(3.14) == 3.14
  assert strToNum("333") == 333
  assert strToNum("0xABC") == 0xABC
  assert strToNum("0xabc") == 0xabc
  try:
    strToNum("hoge")
    assert False
  except ESSXValueException as err:
    pass




