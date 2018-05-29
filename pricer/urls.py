# -*- coding: utf-8 -*-
"""pricer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from pricer.views.mobile_view import MobileView
from pricer.views.order_mgmt_view import OrderMgmtView
from django.conf.urls import url
from django.views.generic.base import RedirectView

urlpatterns = [

    path('admin/', admin.site.urls),
    # url(r'$', InvestmentView.as_view(), name='investment'),
    path('mgmt/all_orders/', OrderMgmtView.as_view(), name="mgmt_orders"),
    path('mgmt/order_detail/', OrderMgmtView.as_view(), name="mgmt_detail"),

    # mobile's url
    # path('^hello/$', MobileView.as_view(), name="products_mobile"),
    # url(r'$', MobileView.as_view(), name='MobileView'),
    url(r'^favicon.ico$', RedirectView.as_view(
        url='/static/images/favicon.ico')),
    url(r'^ajax-loader.gif$',
        RedirectView.as_view(url='/static/images/ajax-loader.gif')),  # 有问题？？


    url(r'$', MobileView.as_view(), name='MobileView'),

    # path(r'$', MobileView.as_view(), name="home"),

    # url(r'$', RedirectView.as_view(url='static/favor.html'), name='go-to-zqxt'),

]
