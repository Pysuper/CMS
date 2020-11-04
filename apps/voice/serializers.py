# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author   : Zheng Xingtao
# File     : serializers.py
# Datetime : 2020/11/4 上午9:38


from rest_framework import serializers

from voice.models import Voice


class VoiceSerializer(serializers.Serializer):
    class Meta:
        model = Voice
        fields = "__all__"
