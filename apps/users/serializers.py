# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Zheng Xingtao
# File : serializers
# Datetime : 2020/8/11 下午12:55


from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User, OAuthQQUser
from users.utils import check_save_user_openid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "phone", "email"]


class QQAuthUserSerializer(serializers.Serializer):
    mobile = serializers.RegexField(label="手机号", regex=r"1[3-9]\d{9}")
    password = serializers.CharField(label="密码", min_length=8, max_length=20)
    sms_code = serializers.CharField(label="短信", min_length=6, max_length=6)
    access_token = serializers.CharField(label="token", min_length=1)

    def validate(self, attrs):
        """多字段校验"""
        # 1 获取加密的openid
        access_token = attrs["access_token"]

        # 2 调用方法解密openid,判断是否存在
        openid = check_save_user_openid(access_token)
        if not openid:
            raise serializers.ValidationError("openid失效")

        # 3 获取redis中的短信,判断为空,正确性
        sms_code = attrs["sms_code"]
        mobile = attrs["mobile"]
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_%s" % mobile)
        if not redis_sms_code:
            raise serializers.ValidationError("短信验证码过期")
        if sms_code != redis_sms_code.decode():
            raise serializers.ValidationError("短信验证码错误")

        # 4 通过手机号查询美多用户是否存在,判断密码正确性
        user = None
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            # 5 表示用户存在,判断密码正确性
            if not user.check_password(attrs["password"]):
                raise serializers.ValidationError("密码错误")

        # 6 返回校验之后的内容
        attrs["openid"] = openid
        attrs["user"] = user
        return attrs

    # 重写create方法,创建qq用户
    def create(self, validated_data):
        """validated_data,就上面返回的attrs"""
        # 1 创建qq用户
        oauth_qq = OAuthQQUser()

        # 2 判断用户是否存在,如果存在设置属性,如果不存在直接创建
        user = validated_data["user"]
        if not user:
            user = User.objects.create(
                username=validated_data["mobile"],
                mobile=validated_data["mobile"],
            )
            user.set_password(validated_data["password"])
            user.save()

        # 3 设置qq用户属性
        oauth_qq.openid = validated_data["openid"]
        oauth_qq.user = user
        oauth_qq.save()

        # 4 返回
        return oauth_qq
