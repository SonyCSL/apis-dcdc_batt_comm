# -*- coding: utf-8 -*-

import sys
import serial
import serial.rs485
#import time
import binascii
import copy
try:
    import Adafruit_BBIO.GPIO as GPIO
except:
    print("This IoT board isn't BBB.")

class ESSXRS485(serial.Serial):
  def __init__(self, *args, **kwargs):
    if 'dir_pin' in kwargs:
      self.dir_pin = kwargs['dir_pin']
      kwargs = copy.copy(kwargs)
      del kwargs['dir_pin']
    else:
      self.dir_pin = "P8_9"

    print("dir_pin: {}".format(self.dir_pin))

    super(ESSXRS485, self).__init__(*args, **kwargs)
    if self.dir_pin != "not_used":
      GPIO.setup(self.dir_pin, GPIO.OUT)
      GPIO.output(self.dir_pin, GPIO.LOW)
    self.reset_input_buffer()

#  def read(self, size = 1):
#   GPIO.output(self.dir_pin, GPIO.LOW)
#    res = super(ESSXRS485, self).read(size)
#    if res != None:
#        print("READ LEN={}".format(len(res)))
#        print("READ LEN={}".format(binascii.hexlify(res)))
#    else:
#        print("READ TIMEOUT")
#
#    return res

  def write(self, b):
    if self.dir_pin != "not_used":
        GPIO.output(self.dir_pin, GPIO.HIGH)
    _len = super(ESSXRS485, self).write(b)
    self.flush()
    self.reset_input_buffer()
    if self.dir_pin != "not_used":
        GPIO.output(self.dir_pin, GPIO.LOW)

    return _len

if __name__  == "__main__":
  import sys
  import argparse
  import binascii

  parser = argparse.ArgumentParser()
  parser.add_argument('--device', default = "/dev/ttyO2")
  parser.add_argument('--speed', default = "9600")
  parser.add_argument('command', choices = ['send', 'recv', 'sendrecv'])
  args = parser.parse_args()

  if args.device == "/dev/ttyO2": #for BBB
      a = ESSXRS485(args.device, int(args.speed), dir_pin = 'P8_7')
  elif args.device == "/dev/ttyO4": #for BBB
      a = ESSXRS485(args.device, int(args.speed), dir_pin = 'P8_7')
  elif args.device == "/dev/ttyO5": #for BBB
      a = ESSXRS485(args.device, int(args.speed), dir_pin = 'P8_9')

  if args.command == 'recv':
      print("waiting..")
      print(a.read(8))
  elif args.command == 'send':
      data = b"ABCDEFGH"
      print("sending " + str(len(b"ABCDEFGH")) + " bytes data")
      a.write(data)
  elif args.command == 'sendrecv':
      data = b"ABCDEFGH"
      print("sending " + str(len(b"ABCDEFGH")) + " bytes data")
      a.write(data)
      print("waiting..")
      print(binascii.hexlify(a.read(8)))
      while True:
          print(binascii.hexlify(a.read(1)))
