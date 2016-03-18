# coding=utf-8
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


_default_response = u'输入字母 h 获取帮助 :-)\n当前版本: %s ' % __version__


def default_handler(message, wechat):
    return wechat.response_text(content=_default_response)


def handle_text_message(message, wechat):
    command_text = wechat_bot.COMMANDS.get(message.content.lower(), '')
    command = getattr(wechat_bot, command_text, default_handler)
    return command(message, wechat)


def handle_subscribe_event(message, wechat):
    return wechat.response_text(content=u'感谢您的关注!\n试试输入字母 h')


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
        wechat.parse_data(unicode(request.data, 'utf-8'))
    except ParseError:
        return 'Invalid Message Data'

    handler = _msg_handler.get(wechat.message.__class__.__name__, default_handler)

    return handler(wechat.message, wechat)


