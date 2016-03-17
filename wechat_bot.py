# encoding=utf-8
from __future__ import print_function, unicode_literals

import os
import requests

__author__ = 'guoyong'

_NASA_OPEN_API_KEY = os.environ['NASA_OPEN_API_KEY']


def apod(message, wechat):
    """
    欣赏每日天文美图
    :param message 微信消息
    :param wechat 微信接口
    :return 包含每日天文美图的微信消息
    """

    r = requests.get('https://api.nasa.gov/planetary/apod?api_key=%s' % _NASA_OPEN_API_KEY)
    data = r.json()

    return wechat.response_news([
        {
            'title': data.get('title'),
            'description': u'日期: %s \n说明: %s\n版权: %s' % (
                data.get('date'), data.get('explanation'), data.get('copyright')),
            'picurl': data.get('url'),
            'url': 'http://apod.nasa.gov/apod/',
        }
    ])

