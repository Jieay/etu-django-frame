"""
URL configuration for frame_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from app.views.cas_admin import views as cas_views
from app.views.comm.health_view import GetHealthCheckView
from app.views.user.members_view import APIGetTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gettoken', APIGetTokenView.as_view()),
    path('login/', cas_views.CasLoginView.as_view(), name='cas_ng_login'),
    path('logout/', cas_views.CasLogoutView.as_view(), name='cas_ng_logout'),
    path('health/check', GetHealthCheckView.as_view()),
]

urlpatterns += [
    re_path(r'^api/', include('app.urls')),
    re_path(r'^sub-server/', include('app.sub_urls')),
]