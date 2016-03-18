# encoding=utf-8
from __future__ import print_function, unicode_literals

import StringIO
import io
import pickle

import pytz
import requests

from PIL import Image
from datetime import datetime, timedelta

from wechat_app import app, redis_store

__author__ = 'guoyong'

NASA_OPEN_API_KEY = app.config['NASA_OPEN_API_KEY']
BASE_URL = app.config['BASE_URL']
APOD_CACHE_KEY = app.config['APOD_CACHE_KEY']

COMMANDS = {
    'h': u'打印此帮助信息',
    'apod': u'欣赏每日天文美图',
}


def h(message, wechat):
    """帮助命令"""
    help_text = u'命令列表:\n%s\n更多命令, 敬请期待' % ''.join(
        ['%s - %s\n' % (command, COMMANDS[command]) for command in COMMANDS.keys()])
    return wechat.response_text(content=help_text)


def apod(message, wechat):
    """
    欣赏每日天文美图
    :param message 微信消息
    :param wechat 微信接口
    :return 包含每日天文美图的微信消息
    """

    apod_image_message = redis_store.hgetall(APOD_CACHE_KEY)

    if not apod_image_message:

        r = requests.get('https://api.nasa.gov/planetary/apod?api_key=%s' % NASA_OPEN_API_KEY)

        if r.status_code != 200:
            return wechat.response_text(content=u'图片获取失败, 请稍后再试')

        data = r.json()

        # download APOD
        image_url = data.get('url')

        r = requests.get(image_url, stream=True)
        if r.status_code != 200:
            return wechat.response_text(content=u'图片获取失败, 请稍后再试')

        r.raw.decode_content = True

        image_file = io.BytesIO(r.raw.read())
        im = Image.open(image_file)

        image_w, image_h = im.size
        aspect_ratio = image_w / float(image_h)
        new_width = 360
        new_height = int(new_width / aspect_ratio)

        imaged = im.resize((360, new_height), Image.ANTIALIAS)

        output = StringIO.StringIO()
        imaged.save(output, quality=90, format='jpeg')

        redis_store.set('%s:image' % APOD_CACHE_KEY, output.getvalue())
        output.close()

        now = datetime.now(tz=pytz.UTC)
        tomorrow = now + timedelta(days=1)
        apod_update_time = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern'))

        apod_image_message = {
            'title': data.get('title'),
            'description': u'日期: %s \n图片版权: %s \n数据提供: <open>api.NASA.gov</data>' % (
                data.get('date'), data.get('copyright')),
            'url': 'http://apod.nasa.gov/apod/',
            'picurl': '%s/apod.jpg' % BASE_URL,
        }

        redis_store.hmset(APOD_CACHE_KEY, apod_image_message, int((apod_update_time - now).total_seconds()))

    return wechat.response_news([apod_image_message])

