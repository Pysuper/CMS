# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author   : Zheng Xingtao
# File     : auth.py
# Datetime : 2020/10/29 上午9:19


from django.http.response import HttpResponse
from django.shortcuts import redirect
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

    # 在视图之前执行
    def process_request(self, request):
        """
        客户端发来请求与路由匹配执行之前执行
        返回值是None时，继续向后执行下一个中间件的process_request或路由映射
        返回值是HttpResponse对象时，不执行路由与views函数，直接执行该中间件与其之前的process_response，倒序执行
        """
        print("1.....process_request")
        return

    # 在视图之前执行 顺序执行
    def process_view(self, request, callback, callback_args, callback_kwarg):
        """
        在执行完所有中间件的process_request与路由映射之后，views函数执行之前执行
        执行顺序依然从第一个中间件到最后一个中间件
        callback参数为执行的views函数
        callback_args, callback_kwargs为views函数的参数
        返回值是None时，继续向后执行下一个中间件的process_view或views函数
        返回值是HttpResponse对象时，不执行views函数，直接执行所有中间件的process_response，倒序执行
        """
        # return: 通过了就直接return，不通过就用redirect做跳转
        print("2.....process_view")
        return

    # 视图执行之前 倒序执行
    def process_template_response(self, request, response):
        """
        视图函数返回的对象有一个render()方法（或者表明该对象是一个TemplateResponse对象或等价方法）时，才被执行（并不是views函数最后返回render对象）
        在views执行之后，process_exception执行之前执行
        返回值必须是response
        倒序执行
        """
        print("process_template_response")

    # 引发错误 才会触发这个方法
    def process_exception(self, request, exception):
        """
        process_exception用于捕捉views函数中的异常
        在process_response之前执行
        exception是views函数中产生的异常对象
        返回值是None时继续正常执行
        返回值是HttpResponse对象：不再执行后面的process_exception方法，直接执行process_response
        倒序执行
        """
        return HttpResponse(exception)  # 返回错误信息

    # 基于请求响应
    def process_response(self, request, response):
        """
        在response返回给客户端之前执行，也就值最后经过
        必须返回HttpResponse对象
        """
        print("3.....process_response")  # 在视图之后
        return response


class AuthMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        if request.session.get("vercode"):
            return
