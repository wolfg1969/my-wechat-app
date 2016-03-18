from flask import Flask
from flask_redis import Redis
from wechat_sdk import WechatConf

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

if __name__ == '__main__':
    app.run()
