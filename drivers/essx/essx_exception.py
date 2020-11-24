# -*- coding: utf-8 -*-
import os
import essx
from essx import essx_debug

class ESSXException(Exception):
    """ ESSX例外の基底となるクラス """
    def __init__(self, reason):
        essx_debug.debug_log(reason)
        self.reason = reason

    def __str__(self):
        return self.reason

class ESSXTimeoutException(ESSXException):
    """ タイムアウトが発生したときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXChecksumException(ESSXException):
    """ チェックサムエラーが発生したときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXValueException(ESSXException):
    """ 値が不整合だったときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXParameterException(ESSXException):
    """ 必要なパラメータが無かったときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXDeviceException(ESSXException):
    """ Deviceでエラーが発生したときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXFatalException(ESSXException):
    """ 致命的なエラーが発生したときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)

class ESSXConfigException(ESSXException):
    """ 設定ファイルの間違いがあるときの例外クラス """
    def __init__(self, reason):
        ESSXException.__init__(self, reason)
