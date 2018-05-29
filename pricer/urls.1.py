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
    path('mgmt/all_orders', OrderMgmtView.as_view(), name="mgmt_orders"),
    path('mgmt/order_detail', OrderMgmtView.as_view(), name="mgmt_detail"),

    # mobile's url
    path('mobile/all_products', MobileView.as_view(), name="products_mobile"),
    path('mobile/update_chart', MobileView.as_view(), name="order_mobile"),
    path('mobile/clear_cart', MobileView.as_view(), name="clear_cart_mobile"),
    path('mobile/preview_order', MobileView.as_view(), name="preview_order_mobile"),
    path('mobile/input_customer_info', MobileView.as_view(), name="input_customer_info"),
    path('mobile/save_order', MobileView.as_view(), name="save_order_mobile"),

    path(r'$', MobileView.as_view(), name="home"),

    # url(r'$', RedirectView.as_view(url='static/favor.html'), name='go-to-zqxt'),

]
