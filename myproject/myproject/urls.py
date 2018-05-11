"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from myapp import views as basic_views
from django.urls import include, path

urlpatterns = [
    url(r'^signup/$', basic_views.signup, name='signup'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout,{'template_name': 'registration/logout.html'}, name='logout'),
    path('home/<str:country_code>/', basic_views.main_page, name='home'),
    url(r'^home/$', basic_views.main_page, name='home'),
    url(r'^admin/', admin.site.urls),
    path('charts/<str:country_code>/', basic_views.charts, name='charts'),
]
