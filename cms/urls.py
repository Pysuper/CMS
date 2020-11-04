from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView

urlpatterns = [
    url('admin/', admin.site.urls),

    url(r'^$', TemplateView.as_view(template_name='base_2.html'), name='index'),  # index页面
    url(r'^favicon\.ico$', RedirectView.as_view(url=r'static/img/favicon.ico')),  # favicon图标

    url(r'^users/', include(('users.urls', "user"), namespace="users")),
]
