# coding=utf-8

import StringIO
import hashlib
import io

import pytz
import requests

from PIL import Image
from datetime import datetime, timedelta

from wx_app import app, redis_store

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
    now = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')

    cache_key = '%s:%s' % (APOD_CACHE_KEY, yesterday)
    apod_image_message = redis_store.hgetall(cache_key)

    app.logger.debug(apod_image_message)

    if not apod_image_message:

        app.logger.info('get new apod')

        r = requests.get('https://api.nasa.gov/planetary/apod?api_key=%s&date=%s' % (NASA_OPEN_API_KEY, yesterday))

        if r.status_code != 200:
            return wechat.response_text(content=u'图片获取失败, 请稍后再试')

        data = r.json()

        title = data.get('title')
        apod_date = data.get('date')

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

        m = hashlib.md5()
        m.update('%s:%s' % (apod_date, title))
        image_cache_key = m.hexdigest()
        redis_store.set(image_cache_key, output.getvalue())
        output.close()

        apod_image_message = {
            'title': title,
            'description': u'日期: %s \n图片版权: %s \n数据提供: <open>api.NASA.gov</data>' % (
                apod_date, data.get('copyright', 'Public')),
            'url': 'http://apod.nasa.gov/apod/',
            'picurl': '%s/apod-%s.jpg' % (BASE_URL, image_cache_key)
        }

        redis_store.hmset(cache_key, apod_image_message)
        redis_store.expire(cache_key, 86400)

    return wechat.response_news([apod_image_message])
