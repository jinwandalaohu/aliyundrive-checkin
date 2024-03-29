import requests, traceback
from bs4 import BeautifulSoup
import base64, json, yaml
from tenacity import retry, stop_after_attempt, wait_random
from collections import defaultdict
import socket
import urllib3


def allowed_gai_family():
    return socket.AF_INET


urllib3.util.connection.allowed_gai_family = allowed_gai_family

# 会不定时更新域名，记得Sync fork
login_url = 'https://ikuuu.pw/auth/login'
check_url = 'https://ikuuu.pw/user/checkin'
info_url = 'https://ikuuu.pw/user/profile'
node_url = 'https://ikuuu.pw/user/node'
free_url = "https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
header = {
    'origin': 'https://ikuuu.pw',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
success = 'OK'


def clash_checkin(message_token: dict):
    session = login_in_ikuuu(message_token)
    content = check_in(session)
    all_node_list = []
    all_node_list.extend(grab_subscribe(session))
    # all_node_list.extend(grab_free_server_list())
    build_sub_yaml(all_node_list)
    return content


def login_in_ikuuu(message_token: dict) -> requests.Session:
    session = requests.session()
    # 配置用户名（一般是邮箱）
    email = message_token.get('ikuuu_email')
    # 配置用户名对应的密码 和上面的email对应上
    passwd = message_token.get('ikuuu_passwd')
    data = {
        'email': email,
        'passwd': passwd
    }
    err_msg = ''
    try:
        response = json.loads(session.post(url=login_url, headers=header, data=data).text)
        err_msg = response['msg']
        # 获取账号名称
        session.get(url=info_url, headers=header)
        return session
    except Exception as e:
        print('签到失败' + '\n' + err_msg)
        raise e


def check_in(session: requests.Session) -> str:
    try:
        # 进行签到
        result = json.loads(session.post(url=check_url, headers=header).text)
        msg = result['msg']
        return msg
    except Exception as e:
        print('签到失败')
        raise e


def grab_subscribe(session: requests.Session) -> list[dict]:
    @retry(stop=stop_after_attempt(10), wait=wait_random(min=10, max=30))
    def call():
        print('获取订阅信息....')
        return session.get(url=node_url, headers=header).text

    server_dict_list: list[dict] = []
    try:
        html_doc = call()
        soup = BeautifulSoup(html_doc, 'html.parser')
        code_list = soup.find_all('code')
        # sub_doc = '\n'.join([code.text for code in code_list if code.text.startswith('vmess:')])
        # doc = base64.b64encode(sub_doc.encode('utf-8')).decode('utf-8')
        for code in [code.text for code in code_list if code.text.startswith('vmess:')]:
            one_sub_txt = base64.b64decode(code[8:].encode('utf-8')).decode('utf-8')
            sub_dict = json.loads(one_sub_txt)
            server_dict_list.append(sub_dict)
        print(server_dict_list)
        return server_dict_list
    except Exception as e:
        print(str(e))
        traceback_info = traceback.format_exc()
        print(traceback_info)
        return server_dict_list


def grab_free_server_list() -> list[dict]:
    @retry(stop=stop_after_attempt(10), wait=wait_random(min=10, max=30))
    def call():
        print("尝试获取免费节点列表...")
        session = requests.session()
        return session.get(url=free_url, headers={}).text

    vmess_list = []
    try:
        res_base64 = call()
        sub_list = base64.b64decode(res_base64.encode('utf-8')).decode('utf-8')
        for code in sub_list.split("\n"):
            if code.startswith("vmess"):
                one_sub_txt = base64.b64decode(code[8:].encode('utf-8')).decode('utf-8')
                sub_dict = json.loads(one_sub_txt)
                vmess_list.append(sub_dict)
        print(vmess_list)
        return vmess_list
    except Exception as e:
        print(e)
        traceback_info = traceback.format_exc()
        print(traceback_info)
        return vmess_list


def build_sub_yaml(node_dict_list: list[dict]):
    with open("template.yaml", encoding="utf-8") as file:
        file_data = file.read()
    yaml_object = yaml.load(file_data, yaml.FullLoader)
    proxies = yaml_object["proxies"]
    proxies.clear()
    proxy_groups = yaml_object["proxy-groups"]
    proxy_groups.clear()
    proxy_group = {'name': "PROXY", "type": "select", "proxies": []}
    proxy_group["proxies"].append("url_test")
    proxy_group_1 = {'name': "url_test", "type": "url-test", "url": "http://cp.cloudflare.com/generate_204",
                     "interval": 1800,
                     "proxies": []}

    # 防止name冲突， 缓存
    name_dict = defaultdict(int)
    for server in node_dict_list:
        ps_name = server["ps"]
        name_dict[ps_name] = name_dict[ps_name] + 1
        if name_dict[ps_name] > 1:
            ps_name = ps_name + "-" + str(name_dict[ps_name] - 1)
        host = server["add"] if server.get("host") is None or server.get("host") == '' or server.get("host") == 'null' else server.get("host")
        proxy = {"name": ps_name, "type": "vmess", "server": host, "port": server["port"],
                 "uuid": server["id"], "alterId": server["aid"], "cipher": "auto",
                 "tls": True if server['tls'] else False, "udp": True}
        # proxy["ws-opts"]["path"] = server["path"]
        yaml_object["proxies"].append(proxy)
        proxy_group["proxies"].append(ps_name)
        proxy_group_1["proxies"].append(ps_name)
    proxy_groups.append(proxy_group)
    proxy_groups.append(proxy_group_1)
    print(yaml_object)
    with open("ikuuu_sub.txt", "w", encoding="utf-8") as file:
        yaml.dump(yaml_object, file, encoding="utf-8", allow_unicode=True)


if __name__ == '__main__':
    # clash_checkin({'ikuuu_email': 'wanghe6363@gmail.com', 'ikuuu_passwd': 'QHUY%$#gyf675'})
    # get_free_server_list()
    # name_dict = defaultdict(int)
    # name_dict['name'] = name_dict['name'] + 1
    pass
