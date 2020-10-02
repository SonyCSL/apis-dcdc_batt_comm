# apis-dcdc_batt_comm

## Introduction
dcdc_batt_commはapis-mainからの指示に従って実際にハードウェアを制御し電力融通を
実現するためのDevice Driverである。(図2-1参照) 制御対象のDCDC Converterとして
TDKラムダ製のEZA2500を想定し、RS485を使用してTDKラムダ製独自プロトコルにより通信を行う。
制御対象のバッテリはRS485上でModbus RTU通信プロトコルを使用して通信を行う想定で作られている。
(レジスタマップはSony CSL開発の独自仕様)  dcdc_batt_comm上にはPython Bottleを
利用してWeb Serverが立っている。apis-mainとの通信はそのWeb Serverを利用して
Sony CSL開発のWeb APIを介して通信を行う。(apis-mainとのWeb APIの仕様に関しては
apis-main仕様書を参照すること。)


## Getting Started


## Usage


## Documentation


## License


## Notice
