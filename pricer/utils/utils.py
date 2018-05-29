# -*- coding: utf-8 -*-
import urllib.parse as urlparse
import json
from pricer.constants import INIT_CART


def parse_get_params(request):
    query_string = request.environ['QUERY_STRING']
    return urlparse.parse_qs(query_string)


def get_session_cart(request, dumps=False):
    cart = json.loads(request.session.get('cart', json.dumps(INIT_CART)))
    # session中存放的所有key，都变成了str型。这里需要转成int型
    cart = {int(k): v for k, v in cart.items()}
    return json.dumps(cart) if dumps else cart
