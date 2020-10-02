#!/usr/bin/env ruby
# coding: utf-8
#
require 'yaml'
require 'erb'

def camelize(str)
  str.split('_').map{|e| e.capitalize}.join
end

def str2opts(optstr)
  opts = {}
  return opts if optstr.nil?
  optstr = optstr.sub(/^"/, '')
  optstr = optstr.sub(/"$/, '')
  (optstr ? optstr.split(/,/) : []).each do |opt|
    if opt.match(/^Q(\d+)/)
      opts[:q] = $1
    end
    if opt.match(/^([\d\.]+)\/([\d\.]+)\-([\d\.]+)\/([\d\.]+)/)
      opts[:min] = $1
      opts[:max] = $3
      opts[:ratings] = $2
    end
    if opt.match(/^\/([\d\.]+)/)
      opts[:min] = 'None'
      opts[:max] = 'None'
      opts[:ratings] = $1
    end
  end
  opts
end

yaml = YAML.load(ARGF.read)

print <<"EOF"
# -*- coding: utf-8 -*-

from struct import pack, unpack
import os
from essx import essx_debug
from essx.essx_exception import ESSXDeviceException, ESSXValueException, ESSXParameterException, ESSXException
import eza2500_base
import eza2500_util

EOF

yaml.each do |conf|
  name = conf['name']
  klass = conf['class']
  command = conf['command']

  send_len = 0
  ack_len = 0

  conf['send'].each do |req|
    (sym, typ, val) = req.split(/ /)
    send_len += 1 if typ == 'B'
    send_len += 2 if typ == 'H'
    send_len += 2 if typ == 'h'
  end
  conf['ack'].each do |req|
    (sym, typ, val) = req.split(/ /)
    ack_len += 1 if typ == 'B'
    ack_len += 2 if typ == 'H'
    ack_len += 2 if typ == 'h'
  end

  send_syms = []
  send_packstr = 'BBBBB'
  send_packsym = ['0x05', 'self.CMD_LEN', 'ad1', 'ad2', command]
  send_convs = []
  send_debug_statements = []

  ack_syms = []
  ack_packstr = ''
  ack_packsym = []
  ack_convs = []
  ack_debug_statements = []

  nak_syms = []
  nak_packstr = ''
  nak_packsym = []


  conf['send'].each do |req|
    (sym, typ, opt) = req.split(/ /)
    opts = str2opts(opt)

    send_packstr += typ
    send_packsym.push "_#{sym}"
    send_syms.push sym
    if opts[:ratings]
      mean = (opts[:min].to_f + opts[:max].to_f) / 2
      send_debug_statements.push "_#{sym} = #{mean}"
    else
      send_debug_statements.push "_#{sym} = 0"
    end
    if opts[:q]
      send_convs.push "_#{sym} = int(eza2500_util.q_normalize(_#{sym}, #{opts[:q]}, '#{opts[:ratings]}', '#{opts[:min]}', '#{opts[:max]}', '#{sym}'))"
    end
    send_debug_statements.push "params['#{sym}'] = _#{sym}"
  end

  conf['ack'].push("chksum H")
  conf['nak'].push("chksum H")
  conf['ack'].each do |req|
    (sym, typ, opt) = req.split(/ /)
    opts = str2opts(opt)

    ack_packstr += typ
    ack_packsym.push "_#{sym}"
    ack_syms.push sym
    if opts[:ratings]
      mean = (opts[:min].to_f + opts[:max].to_f) / 2
      ack_debug_statements.push "_#{sym} = #{mean}"
    else
      ack_debug_statements.push "_#{sym} = 0"
    end
    if opts[:q]
      opts[:min] = "None" unless opts[:min]
      opts[:max] = "None" unless opts[:max]
      ack_convs.push "_#{sym} = eza2500_util.q_denormalize(_#{sym}, #{opts[:q]}, '#{opts[:ratings]}', '#{opts[:min]}', '#{opts[:max]}', '#{sym}')"
      ack_debug_statements.push "_#{sym} = int(eza2500_util.q_normalize(_#{sym}, #{opts[:q]}, '#{opts[:ratings]}', '#{opts[:min]}', '#{opts[:max]}', '#{sym}'))"
    end
  end

  conf['nak'].each do |req|
    (sym, typ, val) = req.split(/ /)
    nak_packstr += typ
    nak_packsym.push "_#{sym}"
    nak_syms.push sym
  end

  erbstr = open("tmpl.erb").read
  erb = ERB.new(erbstr, 0, "-")
  erb.run(binding)
end

print <<"EOF"

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
EOF

yaml.each do |conf|
  klass = conf['class']

print <<"EOF"
  try:
    #{camelize(klass)}.unit_test(dev)
  except ESSXException as err:
    print(err.reason)
    raise err
EOF
end

