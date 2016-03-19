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


@app.route('/apod.jpg', methods=['GET'])
def apod_image():

    key = '%s:image' % app.config['APOD_CACHE_KEY']
    apod_image = redis_store.get(key)

    if not apod_image:
        return 'APOD Not Found', 404

    response = make_response(apod_image)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@app.route('/')
def index():
    return 'hello, world'
