import requests, json, re, os
from bs4 import BeautifulSoup
import time, random, base64


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
    node_url = 'https://ikuuu.pw/user/node'

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
        # info = "".join(re.findall('<span class="user-name text-bold-600">(.*?)</span>', info_html, re.S))
        # print(info)
        # 进行签到
        # result = json.loads(session.post(url=check_url, headers=header).text)
        # print(result['msg'])
        # content = result['msg']
        time.sleep(random.randint(3, 5))
        node_html = session.get(url=node_url, headers=header).text
        grab_subscribe(node_html)

        # 进行推送
        # return content
    except:
        content = '签到失败' + '\n' + err_msg
        return content


def grab_subscribe(html_doc: str):
    soup = BeautifulSoup(html_doc, 'html.parser')
    code_list = soup.find_all('code')
    sub_doc = '\n'.join([code.text for code in code_list if code.text.startswith('vmess:')])
    doc = base64.b64encode(sub_doc.encode('utf-8')).decode('utf-8')
    with open('ikuuu_sub.txt', 'w', encoding='utf-8') as file:
        file.write(doc)


if __name__ == '__main__':
    check_in({'ikuuu_email': 'wanghe6363@gmail.com', 'ikuuu_passwd': 'QHUY%$#gyf675'})
