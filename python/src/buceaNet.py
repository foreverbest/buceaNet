
class Data:
    def __init__(self, action: str, name: str, password: str):
        from random import random
        from math import floor
        if action == "get_online_info":
            k = floor(random() * (100000 + 1))
            self.data = {"action": "get_online_info", "key": str(k)}
        else:
            self.data = {
                "action": action,
                "username": name,
                "password": password,
                "ac_id": 1,
                "save_me": 0,
                "ajax": 1,
            }

    def values(self):
        return self.data


# 操作
def process(action: str, name: str, password: str):
    from math import floor
    from requests import post
    post_data = Data(action, name, password).values()
    result = post("http://10.1.1.131:901/include/auth_action.php", data=post_data)
    result.encoding = result.apparent_encoding

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
        from math import pow
        n = pow(10, count)
        t = floor(num * n)
        return t / n
    
    if action == "login":
        login_info = result.text.split(",")
        print(login_info[0])
    elif action == "logout":
        print(result.text)
    elif action == "get_online_info":
        online_info = result.text.split(",")
        if len(online_info) == 1:
            print(online_info[0])
        else:
            print("已用流量：{}".format(format_flux(int(online_info[0]))))
            print("已用时长：{}".format(format_time(int(online_info[1]))))
            print("账户余额：￥{}".format(online_info[2]))
            print("IP地址：{}".format(online_info[5]))


# 检测网络状态
def status():
    from os import system
    extranet_code = system("ping www.baidu.com>nul")
    intranet_code = system("ping 10.1.1.131>nul")
    if extranet_code:
        if intranet_code:
            print("内网都上不去，网线插好了吗？")
        else:
            print("无法访问外网，登录校园网了吗？")
        return True
    else:
        print("网络畅通，一切正常")
        return False

def TestCase(args: list):
    def help_menu():
        print("用法: buceaNet <option> [arguments]")
        print("option:")
        print("  login <username> <password> - 登录")
        print("  logout <username> <password> - 注销")
        print("  info - 显示在线账户信息")

    if len(args) < 2:
        help_menu()
        exit()
    if args[1] == "login":
        process("login", args[2], args[3])
    elif args[1] == "logout":
        process("logout", args[2], args[3])
    elif args[1] == "info":
        process("get_online_info", None, None)
    else:
        help_menu()

def auto_login(begin_time: int, end_time: int, username: str, passwd: str):
    from time import sleep, localtime
    busy_delay = 300
    free_delay = 3600
    while True:
        current_time = localtime()[3]
        if begin_time <= current_time < end_time:
            if status:
                process("login", username, passwd)
            sleep(busy_delay)
        else:
            if status:
                process("login", username, passwd)
            sleep(free_delay)


if __name__ == "__main__":
    from sys import argv
    TestCase(argv)
    # auto_login(2, 4, None, None)
