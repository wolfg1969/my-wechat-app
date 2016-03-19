# coding=utf-8
from flask import Flask
from flask.ext.redis import FlaskRedis
from redis import StrictRedis
from wechat_sdk import WechatConf

app = Flask(__name__)
app.config.from_envvar('MY_WECHAT_APP_SETTINGS')
redis_store = FlaskRedis.from_custom_provider(StrictRedis, app)

wechat_conf = WechatConf(
    token=app.config['WX_TOKEN'],
    appid=app.config['WX_APP_ID'],
    appsecret=app.config['WX_APP_SECRET'],
    encrypt_mode=app.config['WX_ENCRYPT_MODE'],
    encoding_aes_key=app.config['WX_ENCODING_AES_KEY']
)
