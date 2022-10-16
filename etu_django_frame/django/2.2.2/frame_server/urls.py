"""frame_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


DRF_TITLE = "PDF脚手架"

schema_view = get_schema_view(
   openapi.Info(
      title="{} API".format(DRF_TITLE),
      default_version='v1',
      description="项目接口文档",
      terms_of_service="https:xxx.xxx.com.cn",
      contact=openapi.Contact(email="1016900854@qq.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


from app.views.cas_admin import views as cas_views
from app.views.comm.health_view import GetHealthCheckView
from app.views.user.members_view import APIGetTokenView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('gettoken', APIGetTokenView.as_view()),
    path('login/', cas_views.CasLoginView.as_view(), name='cas_ng_login'),
    path('logout/', cas_views.CasLogoutView.as_view(), name='cas_ng_logout'),
    re_path(r'health/check', GetHealthCheckView.as_view()),
]

if settings.DEBUG is True:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view().without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view().with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view().with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

urlpatterns += [
    re_path(r'^api/', include('app.urls')),
]