# encoding=utf-8
from __future__ import print_function, unicode_literals

import os

import io
import requests
from PIL import Image

__author__ = 'guoyong'

NASA_OPEN_API_KEY = os.environ['NASA_OPEN_API_KEY']
STATIC_BASE_URL = os.environ['STATIC_BASE_URL']
STATIC_DIR = os.environ['STATIC_DIR']


def apod(message, wechat):
    """
    欣赏每日天文美图
    :param message 微信消息
    :param wechat 微信接口
    :return 包含每日天文美图的微信消息
    """

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
    # shutil.copyfileobj(r.raw, f)

    image_file = io.BytesIO(r.raw.read())
    im = Image.open(image_file)

    image_w, image_h = im.size
    aspect_ratio = image_w / float(image_h)
    new_width = 360
    new_height = int(new_width / aspect_ratio)

    imaged = im.resize((360, new_height), Image.ANTIALIAS)
    imaged.save('%s/apod.jpg' % STATIC_DIR, quality=90)

    return wechat.response_news([
        {
            'title': data.get('title'),
            'description': u'日期: %s \n图片版权: %s \n 数据提供: <open>api.NASA.gov</data>' % (
                data.get('date'), data.get('copyright')),
            'picurl': '%s/apod.jpg' % STATIC_BASE_URL,
            'url': 'http://apod.nasa.gov/apod/'
        }
    ])

