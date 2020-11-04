import datetime
import os
import sys

from utils import log_theme

######################################## Django 基础配置 ########################################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = 'qwe_123123'

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_jwt',
    'rest_framework.authtoken',

    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'middleware.auth.AuthMiddleware'  # 手动实现中间件

]

ROOT_URLCONF = 'cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [  # 模板中间件
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'root',  # 数据库用户密码
        'NAME': 'cms',
        'OPTIONS': {
            'read_default_file': os.path.dirname(os.path.abspath(__file__)) + '/my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES,"
                            "NO_ZERO_IN_DATE,NO_ZERO_DATE,"
                            "ERROR_FOR_DIVISION_BY_ZERO,"
                            "NO_AUTO_CREATE_USER'",
        },
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs/cms.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

CACHES = {  # 可以使用不同的配置，实现读写分离
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://0.0.0.0:6379/0",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": "root"  # redis密码
        }
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

LOGIN_URL = '/login/'
STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')    # TODO: uwsgi + Nginx时, 使用ROOT
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]  # TODO: 使用runserver时候，使用DIRS

AUTH_USER_MODEL = 'users.User'  # 指明使用自定义的用户模型类

CORS_ORIGIN_WHITELIST = (
    'https://127.0.0.1:8001',
    'https://localhost:8001',
    'https://127.0.0.1:8001',
    'http://127.0.0.1:8001',
    'http://localhost:8001',
    'http://192.168.43.230:8001'
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

######################################## DRF 信息配置 ########################################
REST_FRAMEWORK = {

    'EXCEPTION_HANDLER': 'utils.exceptions.exception_handler',  # 异常处理
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination',  # 分页
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_USE_CACHE': 'default',  # 缓存存储
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,  # 缓存时间
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),  # 指明token的有效期
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',  # 指定使用的JWT返回的函数
}

AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',  # JWT用户认证登录
    'django.contrib.auth.backends.ModelBackend'  # Admin用户登录
]

WHITE_REGEX_URL_LIST = [
    "/",
    "/favicon.ico",
    "/user/logout/",
    "/user/sms/",
    "/user/register/",
    "/user/image/code/",
    "/user/login/sms/",
    "/user/login/user/",
    "/users/search/",
    "/users/card/",
]

######################################## Simpleui 配置 ########################################
SIMPLEUI_HOME_INFO = False  # 服务器信息
SIMPLEUI_ANALYSIS = False  # 不收集分析信息
SIMPLEUI_STATIC_OFFLINE = True  # 离线模式
# SIMPLEUI_LOGO = 'http://127.0.0.1:8899/favicon.ico'  # LOGO
SIMPLEUI_ICON = {'Users': 'fab fa-apple', '任务信息': 'fas fa-user-tie'}  # 自定义图标

# SIMPLEUI_CONFIG = {
#     'system_keep': False,
#     'menu_display': ['User'],
#     'dynamic': True,
#     'menus': [
#         {
#             'app': 'User',
#             'name': 'User',
#             'icon': 'fa fa-audio-description',
#             'models': [
#                 {'name': '抱怨工况', 'icon': 'far fa-circle', 'url': 'audio/status/'},
#                 {'name': '抱怨描述', 'icon': 'far fa-circle', 'url': 'audio/description/'},
#                 {'name': '抱怨音频', 'icon': 'far fa-circle', 'url': 'audio/audio/'},
#                 {'name': '抱怨频率', 'icon': 'far fa-circle', 'url': 'audio/frequency/'},
#             ]
#         }
#     ]
# }

######################################## 验证码、短信配置 ########################################
# 图片验证码中字体文件的路径
TTF_PATH = os.path.join(BASE_DIR, 'static/ttf/')
SMS_TEMPLATES = {
    "register": "682844",
    "login": "682844",
    "update": "682844",
    "more": ["682844", "682843", "682840"]
}

TENCENT_SMS_APPID = 1400407994
TENCENT_SMS_APPKEY = "0dd1c9e4004fe503700c08d4e4d5098e"
TENCENT_SMS_SIGN = "郑兴涛个人公众号"

######################################## QQ 登录配置 ########################################
QQ_CLIENT_ID = '1111087317'  # ID
QQ_CLIENT_SECRET = 'jS5yEvAmur7pXGMp'  # 密钥
QQ_REDIRECT_URI = 'http://www.xxxx.xxx/oauth_callback.html'  # 回调域