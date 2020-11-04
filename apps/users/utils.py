import datetime

from django.contrib.auth.backends import ModelBackend
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User
from utils import encrypt


# 用户名或者工号登录
def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    try:
        user = User.objects.get(username=account)  # 帐号为用户名
    except User.DoesNotExist:
        return None
    else:
        return user


# 自定义用户名工号认证
class UsernameMobileAuthBackend(ModelBackend):
    """处理数据初始化"""

    def authenticate(self, request, username=None, password=None, vercode=None, **kwargs):
        # 在这里使用上面自定义的获取用户信息方法, 拿到用户后校验jwt

        current_code = kwargs.get("code")  # 用户输入的图片验证码，
        print("用户输入的图片验证码:", current_code)
        # if current_code == request.session.get("image_code"):
        user = get_user_by_account(username)
        if user is not None and user.password == encrypt.md5(password):
            return user


# 自定义jwt认证成功返回的数据 ==> 用户登录成功返回的数据
def jwt_response_payload_handler(token, user=None, request=None):
    # 在这里修改用户登录后的配置信息
    user.is_staff = True  # 修改用户登录状态
    user.last_login = str(datetime.datetime.today())  # 修改用户最后登录时间
    user.save()

    # user_info = {
    #     'id': user.id,
    #     'token': token,
    #     'username': user.username,
    # }
    data = {
        "code": 0
        , "msg": "登入成功"
        , "data": {
            'user': user,
            "access_token": token,
        }
    }
    return data


# 后台创建用户的时候用户的密码明文显示 ==> 校验密码错误
@receiver(post_save, sender=User)  # post_save:接收信号的方式，在save后, sender: 接收信号的model
def create_user(sender, instance=None, created=False, **kwargs):
    # 是否新建，因为update的时候也会进行post_save
    if created:
        password = instance.password  # instance相当于user
        instance.set_password(password)
        instance.save()


# 对openid加密
def generate_save_user_openid(openid):
    # 1,创建TJWSSerializer对象
    serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)

    # 2,加密数据
    token = serializer.dumps({"openid": openid})

    # 3,返回
    return token


# 对openid解密
def check_save_user_openid(access_token):
    # 1 创建serializer对象
    serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)

    # 2 解密openid
    dict_data = serializer.loads(access_token)

    # 3 返回
    return dict_data.get("openid")
