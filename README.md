# apis-dcdc_batt_comm

## Introduction
dcdc_batt_commはapis-mainからの指示に従って実際にハードウェアを制御し電力融通を実現するための  
Device Driverである。制御対象のDCDC ConverterとしてTDKラムダ製のEZA2500を想定し、RS485を  
使用してTDKラムダ製独自プロトコルにより通信を行う。  
制御対象のバッテリはRS485上でModbus RTU通信プロトコルを使用して通信を行う想定で作られている。   
(レジスタマップはSony CSL開発の独自仕様)  
dcdc_batt_comm上にはPython Bottleを利用してWeb Serverが立っており、apis-mainとの通信は  
そのWeb Serverを利用してSony CSL開発のWeb APIを介して通信を行う。  

![dcdc_batt_comm](https://user-images.githubusercontent.com/71874910/94906900-40b64200-04da-11eb-84b5-1134cd3d6b36.PNG)

## Installation

Here is how to install apis-dcdc_batt_comm individually.  
This software runs in Python2.7.  

```bash
$ git clone https://github.com/SonyCSL/apis-dcdc_batt_comm.git
$ cd apis-dcdc_batt_comm
$ virtualenv venv
$ . venv/bin/activate
$ sudo pip install -r requirements.txt
$ deactivate
```

## Running

Here is how to run apis-dcdc_batt_comm individually.  

*By default, 2 USB-RS485 converters are required for /dev/ttyUSB0 and /dev/ttyUSB1.  
See apis-dcdc_batt_comm's [Document](https://github.com/SonyCSL/apis-dcdc_batt_comm/blob/master/doc/jp/apis-dcdc_batt_comm_specification.md) for more information.

```bash
$ cd apis-dcdc_batt_comm
$ . venv/bin/activate
$ cd drivers
$ sudo python essx_server.py
```

## Stopping
Here is how to stop apis-dcdc_batt_comm individually.  

```bash
$ cd apis-dcdc_batt_comm/drivers
$ bash stop.sh
$ deactivate
```


## Documentation
&emsp;[apis-dcdc_batt_comm_specification(JP)](https://github.com/SonyCSL/apis-dcdc_batt_comm/blob/master/doc/jp/apis-dcdc_batt_comm_specification.md)


## License
&emsp;[Apache License Version 2.0](https://github.com/oes-github/apis-dcdc_batt_comm/blob/master/LICENSE)


## Notice
&emsp;[Notice](https://github.com/oes-github/apis-dcdc_batt_comm/blob/master/NOTICE.md)
