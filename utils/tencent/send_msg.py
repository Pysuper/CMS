# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/5 下午9:01
# @Author  : Zheng Xingtao
# @File    : send_msg.py.py


from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

from settings.dev import TENCENT_SMS_APPID, TENCENT_SMS_APPKEY, TENCENT_SMS_SIGN, SMS_TEMPLATES


def send_sms_single(phone_num, template_id, template_param_list):
    """
    单条发送短信
    :param phone_num: 手机号
    :param template_id: 腾讯云短信模板ID
    :param template_param_list: 短信模板所需参数列表，例如:【验证码：{1}，描述：{2}】，则传递参数 [888,666]按顺序去格式化模板
    :return:
    """
    appid = TENCENT_SMS_APPID  # 自己应用ID
    appkey = TENCENT_SMS_APPKEY  # 自己应用Key
    sms_sign = TENCENT_SMS_SIGN  # 自己腾讯云创建签名时填写的签名内容(使用公众号的话这个值一般是公众号全称或简称)
    sender = SmsSingleSender(appid, appkey)
    sms_template = SMS_TEMPLATES[template_id]
    try:
        response = sender.send_with_param(86, phone_num, sms_template, template_param_list, sign=sms_sign)
    except HTTPError as e:
        response = {'result': 1000, 'errmsg': "网络异常发送失败"}
    return response


def send_sms_multi(phone_num_list, template_id, param_list):
    """
    批量发送短信
    :param phone_num_list:手机号列表
    :param template_id:腾讯云短信模板ID
    :param param_list:短信模板所需参数列表，例如:【验证码：{1}，描述：{2}】，则传递参数 [888,666]按顺序去格式化模板
    :return:
    """
    appid = TENCENT_SMS_APPID  # 自己应用ID
    appkey = TENCENT_SMS_APPKEY  # 自己应用Key
    sms_sign = TENCENT_SMS_SIGN  # 自己腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）
    sender = SmsMultiSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num_list, template_id, param_list, sign=sms_sign)
    except HTTPError as e:
        response = {'result': 1000, 'errmsg': "网络异常发送失败"}
    return response

# if __name__ == '__main__':
#     result1 = send_sms_single("18895358393", 682840, [666, ])
# print(result1)
# result2 = send_sms_single(["15131255089", "15131255089", "15131255089", ], 682840, [999, ])
# print(result2)
