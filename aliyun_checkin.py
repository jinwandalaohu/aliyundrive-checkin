import os
import re
import argparse
from aliyundrive import Aliyundrive
from message_send import MessageSend


def check_in(message_token: dict) -> str:
    token_string = message_token.get('token_string')
    token_string = token_string.split(',')
    ali = Aliyundrive()
    message_all = []

    for idx, token in enumerate(token_string):
        result = ali.aliyundrive_check_in(token)
        message_all.append(str(result))

        if idx < len(token_string) - 1:
            message_all.append('--')

    message_all = '\n'.join(message_all)
    message_all = re.sub('\n+', '\n', message_all).rstrip('\n')
    print(message_all)
    return message_all
