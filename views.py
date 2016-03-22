# coding=utf-8
from flask import request, make_response
from wechat_sdk import WechatBasic

from wx_app import app, redis_store, wechat_conf

import wx_message_handler

__author__ = 'guoyong'


@app.route('/wx', methods=['GET', 'POST'])
def handle_wechat_msg():

    app.logger.info('handle_wechat_msg')

    wechat = WechatBasic(conf=wechat_conf)

    handler_name = '%s_handler' % request.method.lower()
    dispatch_method = getattr(wx_message_handler, handler_name)

    return dispatch_method(request, wechat)


@app.route('/apod-<image_cache_key>.jpg', methods=['GET'])
def apod_image(image_cache_key):

    image_data = redis_store.get(image_cache_key)

    if image_data is None:
        return 'APOD Not Found', 404

    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@app.route('/')
def index():
    return 'hello, world'
