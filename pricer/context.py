# -*- coding: utf-8 -*-

# 类似tomcat context的东西
from django.conf import settings
from pricer.settings import NGINX_PREFIX


def nginx_prefix(request):
    return {'nginx_prefix': NGINX_PREFIX}
