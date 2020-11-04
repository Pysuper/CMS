from io import BytesIO

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from utils.encrypt import md5
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from users.serializers import QQAuthUserSerializer
from users.forms import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginUserForm
from users.models import User
from utils.image_code import check_code
from settings.base import QQ_CLIENT_ID, QQ_CLIENT_SECRET, QQ_REDIRECT_URI


# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class Register(View):
    """用户注册，使用forms中的钩子进行校验"""

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        form = RegisterModelForm()
        # return render(request, 'user/register.html', {"form": form})
        return render(request, 'user/register.html')

    @staticmethod
    def post(request):
        form = RegisterModelForm(data=request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({"code": 0, "msg": "注册成功", "data": {"url": "/users/login/"}})
        return JsonResponse({"code": 1, "msg": "注册失败", "data": {"error": form.errors}})


class LoginSms(View):
    """短信登录"""

    @staticmethod
    def get(request):
        form = LoginSmsForm()
        print(form)
        return render(request, 'user/login_sms.html', {"form": form})

    @staticmethod
    def post(request):
        form = LoginSmsForm(data=request.POST)  # 使用Form校验的时候，要将request的参数发送到Form中
        if form.is_valid():
            user_obj = form.cleaned_data["phone"]  # 这里获取的就是user的对象==>写入session

            # 登录成功
            request.session["user_id"] = user_obj.id
            request.session.set_expiry(60 * 60 * 24 * 14)

            return JsonResponse({"status": True, "data": "/"})
        return JsonResponse({"status": False, "error": form.errors})


def send_sms(request):
    """发送短信"""
    form = SendSmsForm(request, data=request.GET)
    # 只是校验手机号: 不能为空, 格式是否正确
    if form.is_valid():
        return JsonResponse({"code": 0, "msg": "发送成功", "data": {}})
    return JsonResponse({"code": 1, "msg": "发送失败", "data": {"error": form.errors}})


def image_code(request):
    """生成图片验证码"""
    image_obj, code = check_code()

    # 将code存入session，并设置60s的过期时间
    request.session["image_code"] = code
    request.session.set_expiry(60)

    # 把图片写入到内存中
    stream = BytesIO()
    image_obj.save(stream, 'png')
    return HttpResponse(stream.getvalue())


@method_decorator(csrf_exempt, name="dispatch")
class LoginUser(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        return render(request, 'user/login.html')

    @staticmethod
    def post(request):
        password = md5(request.POST.get("password", None))
        user = User.objects.filter(username=request.POST.get("username")).first()
        if user.password == password:  # 密码输入正确

            # 再获取前端发送的图片验证码
            session_code = request.session.get("image_code")
            request_code = request.POST.get("vercode").upper()
            print(session_code, request_code)
            if session_code:
                if session_code == request_code:  # 登录成功
                    request.session["user_id"] = user.id
                    request.session.set_expiry(60 * 60 * 24 * 14)
                    return JsonResponse(data={
                        "code": 0,
                        "msg": "登入成功!",
                        "data": {"access_token": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"}
                    })
                return JsonResponse(data={
                    "code": 1,
                    "msg": "验证码输入错误！",
                    "data": {"access_token": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"}
                })
            return JsonResponse(data={
                "code": 1,
                "msg": "图片验证码已过期！",
                "data": {"access_token": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"}
            })
        return JsonResponse(data={
            "code": 1,
            "msg": "密码错误！",
            "data": {"access_token": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"}
        })


@method_decorator(csrf_exempt, name="dispatch")
class ForgetUser(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        return render(request, 'user/forget.html')

    @staticmethod
    def post(request):
        print(request.POST)
        return JsonResponse({"code": 0, "msg": "密码找回完成", "data": {"url": "/users/login/"}})


def logout(request):
    request.session.flush()
    return redirect('/users/login/')


# class QQAuthUserView(GenericAPIView):
#     """用户扫码登录的回调处理"""
#     # 1 指定序列化器
#     serializer_class = QQAuthUserSerializer
#
#     def get(self, request):
#         # 提取code请求参数
#         code = request.query_params.get('code')
#         if not code:
#             return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
#         # 创建工具对象
#         oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)
#         try:
#             access_token = oauth.get_access_token(code)
#             # 3 通过access_token获取openid
#             openid = oauth.get_open_id(access_token)
#             # 4 通过openid查询oauthqq对象
#             try:
#                 oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
#             except OAuthQQUser.DoesNotExist:
#                 # ①, 没有项目用户, 也没有OAuthQQUser用户
#                 # ②, 有项目用户, 没有OAuthQQUser用户
#                 # 5 qq用户没有和项目用户绑定过,加密openid,并返回
#                 access_token_openid = generate_save_user_openid(openid)
#                 return Response({"access_token": access_token_openid})
#         except Exception:
#             return Response({"message": "请求qq服务器异常"},
#                             status=status.HTTP_400_BAD_REQUEST)
#         # 6 oauth_qq_user存在,并且绑定过了美多用户
#         user = oauth_qq_user.user
#
#         # 7 组织数据,拼接token,返回响应
#         jwt_payload_handler = JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = JWT_ENCODE_HANDLER
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#         return Response({
#             "user_id": user.id,
#             "username": user.username,
#             "token": token
#         })
#
#     def post(self, request):
#         # 1,获取数据
#         dict_data = request.data
#
#         # 2 获取序列化器,校验数据
#         serializer = self.get_serializer(data=dict_data)
#         serializer.is_valid(raise_exception=True)
#
#         # 3 数据入库
#         oauth_qq = serializer.save()
#
#         # 4 组织,数据返回响应
#         user = oauth_qq.user
#         jwt_payload_handler = JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = JWT_ENCODE_HANDLER
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#         return Response({
#             "user_id": user.id,
#             "username": user.username,
#             "token": token
#         })
#

######################################## TEST ########################################
@method_decorator(csrf_exempt)
def search(request):
    return JsonResponse({
        "code": 0
        , "msg": ""
        , "count": "100"
        , "data": [{
            "keywords": "贤心是男是女"
            , "frequency": 8520
            , "userNums": 2216
        }, {
            "keywords": "Java程序员能找到女朋友吗"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "此表格是静态模拟数据"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }, {
            "keywords": "layui官方教程"
            , "frequency": 666
            , "userNums": 333
        }]
    })


@method_decorator(csrf_exempt)
def card(request):
    return JsonResponse({
        "code": 0
        , "msg": ""
        , "count": "100"
        , "data": [{
            "id": 111
            , "title": "社区开始接受 “赞助商广告” 投放"
            , "username": "贤心"
            , "channel": "公告"
            , "href": "http://fly.layui.com/jie/15697/"
            , "crt": 61632
        }, {
            "id": 222
            , "title": "layui 一周年"
            , "username": "猫吃"
            , "channel": "讨论"
            , "href": "http://fly.layui.com/jie/16622/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "四个月的前端"
            , "username": "fd"
            , "channel": "分享"
            , "href": "http://fly.layui.com/jie/16651/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }, {
            "id": 333
            , "title": "如何评价LayUI和他的作者闲心"
            , "username": "纸飞机"
            , "channel": "提问"
            , "href": "http://fly.layui.com/jie/9352/"
            , "crt": 61632
        }]
    })


@method_decorator(csrf_exempt)
def message_all(request):
    return JsonResponse({
        "code": 0
        , "msg": ""
        , "count": 60
        , "data": [{
            "id": 123
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510363800000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1507447570000
        }]
    })


@method_decorator(csrf_exempt)
def message_notice(request):
    return JsonResponse({
        "code": 0
        , "msg": ""
        , "count": 60
        , "data": [{
            "id": 123
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510363800000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "你好新朋友，感谢使用 layuiAdmin"
            , "time": 1507447570000
        }]
    })


@method_decorator(csrf_exempt)
def message_direct(request):
    return JsonResponse({
        "code": 0
        , "msg": ""
        , "count": 60
        , "data": [{
            "id": 123
            , "title": "贤心发来了一段私信"
            , "time": 1510363800000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1510212370000
        }, {
            "id": 111
            , "title": "贤心发来了一段私信"
            , "time": 1507447570000
        }]
    })
