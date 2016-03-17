#! encoding=utf-8
from __future__ import print_function, unicode_literals
from wechat_sdk.exceptions import ParseError

import wechat_bot

__author__ = 'guoyong'
__version__ = '0.1'


def get_handler(request, wechat):

    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    if wechat.check_signature(signature, timestamp, nonce):
        return echostr
    else:
        return 'Wrong'


_default_response = u'当前版本: %s \n 命令清单: \n apod \n ' % __version__


def default_handler(message, wechat):
    print('default handler')
    return wechat.response_text(content=_default_response)


def handle_text_message(message, wechat):
    command = getattr(wechat_bot, message.content.lower(), default_handler)
    print(message.content.lower(), command)
    return command(message, wechat)


def handle_subscribe_event(message, wechat):
    return wechat.response_text(content=u'感谢您的关注!\n试试输入命令 apod ')


_evt_msg_handler = {
    'subscribe': handle_subscribe_event
}


def handle_event_message(message, wechat):
    handler = _evt_msg_handler.get(message.type, default_handler)
    return handler(message, wechat)


_msg_handler = {
    'TextMessage': handle_text_message,
    'EventMessage': handle_event_message,
}


def post_handler(request, wechat):

    try:
        wechat.parse_data(request.data)
    except ParseError:
        return 'Invalid Message Data'

    handler = _msg_handler.get(wechat.message.__name__, default_handler)

    return handler(wechat.message, wechat)


