import io

from flask import Flask, request, send_file
from flask_redis import Redis
from wechat_sdk import WechatConf, WechatBasic

import wechat_message_handler

app = Flask(__name__)
app.config.from_envvar('MY_WECHAT_APP_SETTINGS')
redis = Redis(app)

wechat_conf = WechatConf(
    token=app.config['WX_TOKEN'],
    appid=app.config['WX_APP_ID'],
    appsecret=app.config['WX_APP_SECRET'],
    encrypt_mode=app.config['WX_ENCRYPT_MODE'],
    encoding_aes_key=app.config['WX_ENCODING_AES_KEY']
)


@app.route('/wx', methods=['GET', 'POST'])
def handle_wechat_msg():

    app.logger.info('handle_wechat_msg')

    wechat = WechatBasic(conf=wechat_conf)

    handler_name = '%s_handler' % request.method.lower()
    dispatch_method = getattr(wechat_message_handler, handler_name)

    return dispatch_method(request, wechat)


@app.route('/apod.jpg', methods=['GET'])
def apod_image():

    redis = app.config.extensions['redis']
    apod_image_message = redis.get(app.config['APOD_CACHE_KEY'])

    if not apod_image_message:
        return 'APOD Not Found', 404

    # response = make_response(image_binary)
    # response.headers['Content-Type'] = 'image/jpeg'
    # response.headers['Content-Disposition'] = 'attachment; filename=apod.jpg'
    # return response
    return send_file(io.BytesIO(apod_image_message['picdata']))

if __name__ == '__main__':
    app.run()
