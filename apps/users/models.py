from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """网站用户"""
    username = models.CharField(max_length=32, db_index=True, unique=True, verbose_name='用户')  # db_index=True 添加索引
    cellphone = models.CharField(max_length=64, verbose_name="电话")

    class Meta:
        ordering = ("id",)
        verbose_name_plural = verbose_name = "用户信息"

    def __str__(self):
        return self.username


class OAuthQQUser(models.Model):
    """
    QQ登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'oauth_qq'
        verbose_name_plural = verbose_name = "QQ用户"
