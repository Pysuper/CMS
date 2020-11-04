# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Zheng Xingtao
# File : encrypt
# Datetime : 2020/8/11 下午1:34

import hashlib
import uuid

from settings.base import SECRET_KEY


def md5(string):
    """
    实现MD5加密
    :param string: 传入的字符串
    :return: 加密后的字符串
    """

    hash_object = hashlib.md5(SECRET_KEY.encode("utf-8"))
    hash_object.update(string.encode("utf-8"))
    return hash_object.hexdigest()


def uid(string):
    """
    生成随机字符串
    :param string: 字符串
    :return: 加密后的随机字符串
    """
    data = "{}-{}".format(str(uuid.uuid4()), string)
    return md5(data)
