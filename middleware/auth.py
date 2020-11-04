# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author   : Zheng Xingtao
# File     : auth.py
# Datetime : 2020/10/29 上午9:19


from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class Tracer(object):
    """
    在中间件中封装tracer对象
    """

    def __init__(self):
        self.user = None


class AuthMiddleware(MiddlewareMixin):
    """
    用户校验的中间件
    1. process_request
    2. process_view
    """

    @staticmethod  # 在视图之前执行
    def process_request(request):
        print("1.....process_request")
        return

    @staticmethod  # 基于请求响应
    def process_response(request, response):
        print("3.....process_response")  # 在视图之后
        return response

    @staticmethod  # 在视图之前执行 顺序执行
    def process_view(request, view, args, kwargs):
        # return: 通过了就直接return，不通过就用redirect做跳转
        print("2.....process_view")
        return
        # return redirect('/')

    @staticmethod  # 引发错误 才会触发这个方法
    def process_exception(request, exception):
        return HttpResponse(exception)  # 返回错误信息
