#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#import sys
#from decimal import Decimal
#from essx.essx_exception import *
from eza_util import calc_check_sum, replace_check_sum, verify_check_sum, q_normalize, q_denormalize

if __name__  == "__main__":
  #単体テストをするにはPYTHONPATHに一つ上のディレクトリを指定すること
  val0 = 200
  val1 = q_normalize(val0, 13, 240)
  val2 =  q_denormalize(val1, 13, 240)
  assert val0 == val2

  val0 = 400
  val1 = q_normalize(val0, 13, 320)
  val2 =  q_denormalize(val1, 13, 320)
  assert val0 == val2

  #上限
  val0 = 306
  val1 = q_normalize(val0, 13, 240, 144, 306)
  val2 =  q_denormalize(val1, 13, 240, 144, 306)
  assert val0 == val2

  #下限
  val0 = 144
  val1 = q_normalize(val0, 13, 240, 144, 306)
  val2 =  q_denormalize(val1, 13, 240, 144, 306)
  assert val0 == val2

  #ランダム
  import random
  for i in range(1000):
    l = random.randint(1, 400)
    h = random.randint(1, 400)
    if l > h:
      t = h
      h = l
      l = t
    r = random.randint(l, h)
    val0 = random.randint(l, h)
    val1 = q_normalize(val0, 13, r, l, h)
    val2 = q_denormalize(val1, 13, r, l, h)
    assert abs(val0 - val2) < 1E-20

  assert calc_check_sum("123456789") == (0x33+0x34+0x35+0x36+0x37)
  assert replace_check_sum("123456789") == "1234567\x09\x01"
  assert verify_check_sum("1234567\x09\x01")
  assert verify_check_sum("123456789") == False


