# -*- coding: utf-8 -*-
from pricer.constants import SESSION_EXPIER_TIME
from pricer.settings import NGINX_PREFIX
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # print('simple:' + request.path)

        if request.path not in ['/mobile/index/',
                                '/mobile/input_register/',
                                '/mobile/activate/',
                                '/mobile/pre_login/',
                                '/mobile/login/',
                                '/mobile/register/']:
            admin = request.session.get('admin_user', None)
            # print(admin)
            if admin:
                request.session.set_expiry(SESSION_EXPIER_TIME)
            else:
                return HttpResponseRedirect(NGINX_PREFIX+'/mobile/index/')
