from requests import post
from math import pow, floor
from random import random

# 登录
def login(name: str, password: str):
    post_data = {
        "action": "login",
        "username": name,
        "password": password,
        "ac_id": 1,
        "save_me": 1,
        "ajax": 1,
    }
    result = post(
        "http://10.1.1.131:901/include/auth_action.php", data=post_data
    )
    result.encoding = result.apparent_encoding
    login_info = result.text.split(",")
    print(login_info[0])

# 注销
def logout(name: str, password: str):
    post_data = {
        "action": "logout",
        "username": name,
        "password": password,
        "ac_id": 1,
        "save_me": 1,
        "ajax": 1,
    }
    result = post(
        "http://10.1.1.131:901/include/auth_action.php", data=post_data
    )
    result.encoding = result.apparent_encoding
    print(result.text)


# 格式化时间
def format_time(sec: int):
    h = floor(sec / 3600)
    m = floor(sec % 3600)
    s = sec % 3600 % 60
    out = ""
    if h < 10:
        out += "0{} : ".format(h)
    else:
        out += "{} : ".format(h)
    if m < 10:
        out += "0{} : ".format(m)
    else:
        out += "{} : ".format(m)
    if s < 10:
        out += "0{}".format(s)
    else:
        out += "{}".format(s)
    return out


# 格式化流量
def format_flux(byte: int):
    if byte > (1000 * 1000):
        return str(format_number((byte / (1000 * 1000)), 2)) + "M"
    if byte > 1000:
        return str(format_number((byte / 1000), 2)) + "K"
    return byte + "b"


# 格式化数字
def format_number(num: int, count: int):
    n = pow(10, count)
    t = floor(num * n)
    return t / n


# 获取信息
def getinfo(username: str):
    k = floor(random() * (100000 + 1))
    post_data = {"action": "get_online_info", "key": str(k)}
    result = post(
        "http://10.1.1.131:903/include/auth_action.php?k={}".format(k), data=post_data
    )
    result.encoding = result.apparent_encoding
    online_info = result.text.split(",")
    if len(online_info) == 1:
        print(online_info[0])
    else:
        print("已用流量：{}".format(format_flux(int(online_info[0]))))
        print("已用时长：{}".format(format_time(int(online_info[1]))))
        print("账户余额：￥{}".format(online_info[2]))
        print("IP地址：{}".format(online_info[5]))


#login("2108570020058", "snipexl1997")
#logout("2108570020058", "snipexl1997")
#getinfo("2108570020058")

