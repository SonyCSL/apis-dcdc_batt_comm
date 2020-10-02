#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#import sys
from decimal import Decimal
from essx.essx_exception import ESSXValueException

def calc_check_sum(data):
  """
  data[2:-2]のチェックサムを計算し返す

  @param data データ。4バイト以上の長さが必要
  @return チェックサム
  """
  cksum = 0
  for i in range(2, len(data) - 2):
    cksum += ord(data[i])
  return cksum % 65536

def replace_check_sum(data):
  """
  data[2:-2]のチェックサムを計算し
  data[-2:]を置き換える

  @param data データ。4バイト以上の長さが必要
  @return 最終2バイトをチェックサムに置き換えたデータ
  """
  cksum = 0
  for i in range(2, len(data) - 2):
    cksum += ord(data[i])
  return data[:-2] + ("%c%c" % (cksum % 256, cksum / 256))

def verify_check_sum(data):
  """
  data[2:-2]のチェックサムを計算し
  data[-2:]と比較する

  @param data データ。4バイト以上の長さが必要
  @return 一致すれば True。そうでなければ False
  """
  cksum = 0
  for i in range(2, len(data) - 2):
    cksum += ord(data[i])
  return data[-2:] == ("%c%c" % (cksum % 256, cksum / 256))

def q_normalize(val, q, ratings, min_val = None, max_val = None, name = "", checkrange = False):
  """
  Qフォーマットで正規化する
  See. EZA§7

  @param val データ
  @param q q値

  @param ratings 定格値
  @param min_val 最小値
  @param max_val 最大値
  @param name エラー発生時に入れる名前

  @return 正規化後の数(整数化さされていないので注意)

  ratings, min_val, max_valはDecimal化されるので文字列で渡してもよい。
  （そのほうが誤差を抑えらえる）
  """
  if checkrange:
    if min_val == "None":
      min_val = None
    if max_val == "None":
      max_val = None

    if min_val != None and Decimal(val) < Decimal(min_val):
      raise ESSXValueException("out of range: " + name + ": " + str(val) + " < " + str(min_val))
    if max_val != None and Decimal(val) > Decimal(max_val):
      raise ESSXValueException("out of range: " + name + ": " + str(val) + " > " + str(max_val))

  return (2 ** q) * Decimal(val) / Decimal(ratings)

def q_denormalize(val, q, ratings, min_val = None, max_val = None, name = "", checkrange = False):
  """
  Qフォーマットで非正規化する
  See. EZA§7

  @param val データ(整数/固定小数点)
  @param q q値
  @param ratings 定格値
  @param min_val 最小値
  @param max_val 最大値

  @return 非正規化後の値

  ratings, min_val, max_valはDecimal化されるので文字列で渡してもよい。
  （そのほうが誤差を抑えらえる）
  """
  if checkrange:
    if min_val == "None":
      min_val = None
    if max_val == "None":
      max_val = None

    if min_val != None:
      n_min_val = int(q_normalize(Decimal(min_val), q, ratings))

    if max_val != None:
      n_max_val = int(q_normalize(Decimal(max_val), q, ratings))

  retval =  Decimal(val) * Decimal(ratings) / 2 ** q

  if checkrange:
    if min_val != None and int(val) < n_min_val:
      raise ESSXValueException("out of range: " + name + " " + str(retval) + " < " + str(min_val))
    if max_val != None and int(val) > n_max_val:
      raise ESSXValueException("out of range: " + name + " " + str(retval) + " > " + str(max_val))

  return retval

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


