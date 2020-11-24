#!/bin/sh

export PYTHONPATH=drivers
export ESSX_LOG_LEVEL=10

for i in \
  drivers/battery_emulator/__init__.py \
  drivers/essx/essx_type_oes.py \
  drivers/eza2500/eza_device.py \
  drivers/eza2500/eza_util.py \
  drivers/eza2500/eza2500_base.py \
  drivers/eza2500/eza2500_device.py \
  drivers/eza2500/eza2500_util.py \
  drivers/eza2500/command*.py \
; do
  echo '####'
  echo '####' $i '####'
  echo '####'
  python $i
done

