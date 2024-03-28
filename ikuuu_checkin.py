import requests, json, re, os


def check_in(message_token: dict) -> str:
    session = requests.session()
    # 配置用户名（一般是邮箱）
    email = message_token.get('ikuuu_email')
    # 配置用户名对应的密码 和上面的email对应上
    passwd = message_token.get('ikuuu_passwd')

    # 会不定时更新域名，记得Sync fork
    login_url = 'https://ikuuu.pw/auth/login'
    check_url = 'https://ikuuu.pw/user/checkin'
    info_url = 'https://ikuuu.pw/user/profile'

    header = {
        'origin': 'https://ikuuu.pw',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    data = {
        'email': email,
        'passwd': passwd
    }
    err_msg = ''
    try:
        response = json.loads(session.post(url=login_url, headers=header, data=data).text)
        err_msg = response['msg']
        # 获取账号名称
        info_html = session.get(url=info_url, headers=header).text
        #     info = "".join(re.findall('<span class="user-name text-bold-600">(.*?)</span>', info_html, re.S))
        #     print(info)
        # 进行签到
        result = json.loads(session.post(url=check_url, headers=header).text)
        print(result['msg'])
        content = result['msg']
        # 进行推送
        return content
    except:
        content = '签到失败' + '\n' + err_msg
        return content
