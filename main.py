import os
import argparse
import aliyun_checkin
import ikuuu_checkin
import message_send


def parse_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('--token_string', type=str, required=True)
    args = parser.parse_args()

    token_string = args.token_string
    pushplus_token = os.environ.get('PUSHPLUS_TOKEN')
    serverChan_sendkey = os.environ.get('SERVERCHAN_SENDKEY')
    weCom_tokens = os.environ.get('WECOM_TOKENS')
    weCom_webhook = os.environ.get('WECOM_WEBHOOK')
    bark_deviceKey = os.environ.get('BARK_DEVICEKEY')
    feishu_deviceKey = os.environ.get('FEISHU_DEVICEKEY')
    ikuuu_email = os.environ.get('EMAIL')
    # 配置用户名对应的密码 和上面的email对应上
    ikuuu_passwd = os.environ.get('IKUUU_PASSWD')
    # server酱

    message_tokens = {
        'pushplus_token': pushplus_token,
        'serverChan_token': serverChan_sendkey,
        'weCom_tokens': weCom_tokens,
        'weCom_webhook': weCom_webhook,
        'bark_deviceKey': bark_deviceKey,
        'feishu_deviceKey': feishu_deviceKey,
        'token_string': token_string,
        'ikuuu_email': ikuuu_email,
        'ikuuu_passwd': ikuuu_passwd
    }
    return message_tokens


if __name__ == '__main__':
    message_toke = parse_args()
    ali_content = aliyun_checkin.check_in(message_toke)
    ikuuu_content = ikuuu_checkin.check_in(message_toke)

    message_all = f"""
[阿里网盘签到]
{ali_content}
    
[ikuuu签到]
{ikuuu_content}
    """
    print(message_all)
    send = message_send.MessageSend()
    send.send_all(message_toke, "签到信息", message_all)

