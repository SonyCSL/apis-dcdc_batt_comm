# -*- coding: utf-8 -*-
class ESSXGlobal:
  saved_params = {
    0: {}
  }

  @classmethod
  def has(cls, unit, key):
    if not unit in cls.saved_params:
      return False
    return key in cls.saved_params[unit]

  @classmethod
  def put(cls, unit, key, value):
    if not unit in cls.saved_params:
      cls.saved_params[unit] = {}
    cls.saved_params[unit][key] = value

  @classmethod
  def get(cls, unit, key):
    if not unit in cls.saved_params:
      return False
    return cls.saved_params[unit][key]

  @classmethod
  def reset(cls, unit):
    cls.saved_params = {
      unit: {}
    }

