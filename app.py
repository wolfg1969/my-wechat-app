from flask import Flask, request
from wechat_sdk import WechatConf, WechatBasic

import wechat_message_handler

app = Flask(__name__)
app.config.from_envvar('MY_WECHAT_APP_SETTINGS')

conf = WechatConf(
    token=app.config['WX_TOKEN'],
    appid=app.config['WX_APP_ID'],
    appsecret=app.config['WX_APP_SECRET'],
    encrypt_mode=app.config['WX_ENCRYPT_MODE'],
    encoding_aes_key=app.config['WX_ENCODING_AES_KEY']
)


@app.route('/wx', methods=['GET', 'POST'])
def handle_wechat_msg():

    wechat = WechatBasic(conf=conf)

    handler_name = '%s_handler' % request.method.lower()
    dispatch_method = getattr(wechat_message_handler, handler_name)

    return dispatch_method(request, wechat)


if __name__ == '__main__':
    app.run()
