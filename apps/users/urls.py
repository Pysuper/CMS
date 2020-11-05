# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/8/6 上午1:06
# @Author  : Zheng Xingtao
# @File    : urls.py.py

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from .views import *

urlpatterns = [
    url(r'^logout/$', logout, name="logout"),
    url(r'^sms/$', send_sms, name="sms"),
    url(r'^code/$', image_code, name="code"),
    url(r'^register/$', Register.as_view(), name="register"),
    # url(r'^login/sms/$', LoginSms.as_view(), name="login_sms"),
    url(r'^login/$', LoginUser.as_view(), name="login"),
    url(r'^forget/$', ForgetUser.as_view(), name="forget"),

    url(r'^authorization/$', obtain_jwt_token, name="authorization"),

    ######################################## TEST ########################################
    url(r'^search/$', message_search, name="search"),
    url(r'^card/$', message_card, name="card"),
    url(r'^all/$', message_all, name="all"),
    url(r'^notice/$', message_notice, name="notice"),
    url(r'^direct/$', message_direct, name="direct"),
    url(r'^task/$', message_task, name="task"),
]
