import io
from flask import request, send_file
from wechat_sdk import WechatBasic

from wechat_app import app, redis_store, wechat_conf

import wechat_message_handler

__author__ = 'guoyong'


@app.route('/wx', methods=['GET', 'POST'])
def handle_wechat_msg():

    app.logger.info('handle_wechat_msg')

    wechat = WechatBasic(conf=wechat_conf)

    handler_name = '%s_handler' % request.method.lower()
    dispatch_method = getattr(wechat_message_handler, handler_name)

    return dispatch_method(request, wechat)


@app.route('/apod.jpg', methods=['GET'])
def apod_image():

    key = '%s:image' % app.config['APOD_CACHE_KEY']
    apod_image_message = redis_store.get(key)

    if not apod_image_message:
        return 'APOD Not Found', 404

    # response = make_response(image_binary)
    # response.headers['Content-Type'] = 'image/jpeg'
    # response.headers['Content-Disposition'] = 'attachment; filename=apod.jpg'
    # return response
    return send_file(io.BytesIO(apod_image_message['picdata']))


@app.route('/')
def index():
    return 'hello, world'
