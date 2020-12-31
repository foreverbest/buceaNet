
_PADCHAR = "="
_ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

def force(msg):
    ret = []
    for w in msg:
        ret.append(ord(w))
    return bytes(ret)

def ordat(msg, idx):
    if len(msg) > idx:
        return ord(msg[idx])
    return 0

def sencode(msg, key):
    l = len(msg)
    pwd = []
    for i in range(0, l, 4):
        pwd.append(
            ordat(msg, i)
            | ordat(msg, i + 1) << 8
            | ordat(msg, i + 2) << 16
            | ordat(msg, i + 3) << 24
        )
    if key:
        pwd.append(l)
    return pwd

def lencode(msg, key):
    l = len(msg)
    ll = (l - 1) << 2
    if key:
        m = msg[l - 1]
        if m < ll - 3 or m > ll:
            return
        ll = m
    for i in range(0, l):
        msg[i] = (
            chr(msg[i] & 0xFF)
            + chr(msg[i] >> 8 & 0xFF)
            + chr(msg[i] >> 16 & 0xFF)
            + chr(msg[i] >> 24 & 0xFF)
        )
    if key:
        return "".join(msg)[0:ll]
    return "".join(msg)

def _getbyte(s, i):
    x = ord(s[i])
    if x > 255:
        print("INVALID_CHARACTER_ERR: DOM Exception 5")
        exit(0)
    return x

def get_xencode(msg, key):
    from math import floor
    if msg == "":
        return ""
    pwd = sencode(msg, True)
    pwdk = sencode(key, False)
    if len(pwdk) < 4:
        pwdk = pwdk + [0] * (4 - len(pwdk))
    n = len(pwd) - 1
    z = pwd[n]
    y = pwd[0]
    c = 0x86014019 | 0x183639A0
    m = 0
    e = 0
    p = 0
    q = floor(6 + 52 / (n + 1))
    d = 0
    while 0 < q:
        d = d + c & (0x8CE0D9BF | 0x731F2640)
        e = d >> 2 & 3
        p = 0
        while p < n:
            y = pwd[p + 1]
            m = z >> 5 ^ y << 2
            m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
            m = m + (pwdk[(p & 3) ^ e] ^ z)
            pwd[p] = pwd[p] + m & (0xEFB8D130 | 0x10472ECF)
            z = pwd[p]
            p = p + 1
        y = pwd[0]
        m = z >> 5 ^ y << 2
        m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
        m = m + (pwdk[(p & 3) ^ e] ^ z)
        pwd[n] = pwd[n] + m & (0xBB390742 | 0x44C6F8BD)
        z = pwd[n]
        q = q - 1
    return lencode(pwd, False)

def get_base64(s):
    i = 0
    b10 = 0
    x = []
    imax = len(s) - len(s) % 3
    if len(s) == 0:
        return s
    for i in range(0, imax, 3):
        b10 = (
            (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8) | _getbyte(s, i + 2)
        )
        x.append(_ALPHA[(b10 >> 18)])
        x.append(_ALPHA[((b10 >> 12) & 63)])
        x.append(_ALPHA[((b10 >> 6) & 63)])
        x.append(_ALPHA[(b10 & 63)])
    i = imax
    if len(s) - imax == 1:
        b10 = _getbyte(s, i) << 16
        x.append(
            _ALPHA[(b10 >> 18)] + _ALPHA[((b10 >> 12) & 63)] + _PADCHAR + _PADCHAR
        )
    elif len(s) - imax == 2:
        b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8)
        x.append(
            _ALPHA[(b10 >> 18)]
            + _ALPHA[((b10 >> 12) & 63)]
            + _ALPHA[((b10 >> 6) & 63)]
            + _PADCHAR
        )
    return "".join(x)

def get_md5(password, token):
    from hmac import new
    from hashlib import md5
    return new(token.encode(), password.encode(), md5).hexdigest()

def get_sha1(value):
    from hashlib import sha1
    return sha1(value.encode()).hexdigest()


import requests, time, re


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0 WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36"
}
init_url = "http://10.1.1.131"
get_challenge_api = "http://10.1.1.131/cgi-bin/get_challenge"
srun_portal_api = "http://10.1.1.131/cgi-bin/srun_portal"
rad_userinfo_api = "http://10.1.1.131/cgi-bin/rad_user_info"
n = "200"
type = "1"
ac_id = "1"
enc = "srun_bx1"

def get_chksum():
    chkstr = token + username
    chkstr += token + hmd5
    chkstr += token + ac_id
    chkstr += token + ip
    chkstr += token + n
    chkstr += token + type
    chkstr += token + i
    return chkstr

def get_info():
    info_temp = {
        "username": username,
        "password": password,
        "ip": ip,
        "acid": ac_id,
        "enc_ver": enc,
    }
    i = re.sub("'", '"', str(info_temp))
    i = re.sub(" ", "", i)
    return i

def init_getip():
    global ip
    init_res = requests.get(init_url, headers=header)
    if DEBUG_MODE:
        if SHOW_IP:
            print("初始化获取ip")
    ip = re.search('ip(\s*):(\s*)"(.*)"', init_res.text).group(3)
    if DEBUG_MODE:
        if SHOW_IP:
            print("ip:" + ip)

def get_token():
    if DEBUG_MODE:
        if SHOW_TOKEN:
            print("获取token")
    global token
    get_challenge_params = {
        "callback": "jQuery112404953340710317169_" + str(int(time.time() * 1000)),
        "username": username,
        "ip": ip,
        "_": int(time.time() * 1000),
    }
    get_challenge_res = requests.get(
        get_challenge_api, params=get_challenge_params, headers=header
    )
    token = re.search('"challenge":"(.*?)"', get_challenge_res.text).group(1)
    if DEBUG_MODE:
        if SHOW_TOKEN:
            print(get_challenge_res.text)
            print("token为:" + token)

def encode():
    global i, hmd5, chksum
    i = get_info()
    i = "{SRBX1}" + get_base64(get_xencode(i, token))
    hmd5 = get_md5(password, token)
    chksum = get_sha1(get_chksum())
    if DEBUG_MODE:
        print("所有加密工作已完成")

def init_work():
    init_getip()
    get_token()
    encode()

def login():
    srun_portal_params={
    'callback': 'jQuery11240645308969735664_'+str(int(time.time()*1000)),
    'action':'login',
    'username':username,
    'password':'{MD5}'+hmd5,
    'ac_id':ac_id,
    'ip':ip,
    'chksum':chksum,
    'info':i,
    'n':n,
    'type':type,
    'os':'windows+10',
    'name':'windows',
    'double_stack':'0',
    '_':int(time.time()*1000)
    }
    srun_portal_res=requests.get(srun_portal_api,params=srun_portal_params,headers=header)
    if DEBUG_MODE:
        if SHOW_SRUN_PORTAL_INFO:
            print(srun_portal_params)
            print(srun_portal_res.text)
    if (re.search("E0000", srun_portal_res.text)):
        print("登录成功")
    if (re.search("E2531", srun_portal_res.text)):
        print("用户不存在")
    if (re.search("E2553", srun_portal_res.text)):
        print("账号或密码错误")
    elif (re.search("ip_already_online_error", srun_portal_res.text)):
        print("已经是在线状态，当前设备IP地址：{}".format(ip))
    else:
        print("未知错误")


def logout():
    srun_portal_params = {
        'callback': 'jQuery112407038589071100492_'+str(int(time.time()*1000)),
        'action': 'logout',
        'username': username,
        #'password': '{MD5}'+hmd5,
        'ac_id': ac_id,
        'ip': ip,
        #'chksum': chksum,
        #'info': i,
        #'n': n,
        #'type': type,
        #'os': 'windows+10',
        #'name': 'windows',
        #'double_stack': '0',
        '_': int(time.time()*1000)
    }
    srun_portal_res = requests.get(
        srun_portal_api, params=srun_portal_params, headers=header)
    if DEBUG_MODE:
        if SHOW_SRUN_PORTAL_INFO:
            print(srun_portal_params)
            print(srun_portal_res.text)
    if (re.search('"error":"ok"', srun_portal_res.text)):
        print("注销成功")
    elif (re.search('"error":"login_error"', srun_portal_res.text)):
        print("已经是离线状态，当前设备IP地址：{}".format(ip))
    else:
        print("未知错误")

def format_flux(flux):
    res = int(flux)
    res /= 1024
    if res < 1024:
        return str(round(res, 2)) + ' kb'
    res /= 1024
    if res < 1024:
        return str(round(res, 2)) + ' Mb'
    return str(round(res/1024, 2)) + ' Gb'

def format_time(time):
    h = int(int(time) / 60**2)
    m = int((int(time) % 60**2) / 60)
    s = int((int(time) % 60**2) % 60)
    return "{} 小时 {} 分 {} 秒".format(h, m, s)

def get_status():
    result = requests.get(rad_userinfo_api)
    if DEBUG_MODE:
        if SHOW_USER_INFO:
            print(result)
            print(result.text)
    if (re.search("not_online_error", result.text)):
        print("当前为离线状态，请登录")
        return None
    else:
        info_list = result.text.split(',')
        if (not len(info_list) == 22):
            print("错误 -> 无法获取正确的数据列表")
            return None
        username     = info_list[0]
        remain_flux  = info_list[6]
        time_used    = info_list[7]
        client_ip    = info_list[8]
        remain_money = info_list[11]
        return [username, remain_flux, time_used, client_ip, remain_money]

def help_menu():
    print("用法：{} <command> <args>".format(argv[0].split('/')[-1]))
    print("login <学号> <密码>   - 登录")
    print("logout <学号> <密码>  - 注销")
    print("info                - 查看在线状态")

def auto_login(begin_time: int, end_time: int, username: str, passwd: str):
    from os import system
    from time import sleep, localtime
    busy_delay = 300
    free_delay = 3600
    while True:
        current_time = localtime()[3]
        if begin_time <= current_time < end_time:
            if system("ping www.baidu.com>nul"):
                init_work()
                login()
            sleep(busy_delay)
        else:
            if system("ping www.baidu.com>nul"):
                init_work()
                login()
            sleep(free_delay)

if __name__ == '__main__':
    global username, password
    global DEBUG_MODE, SHOW_IP, SHOW_TOKEN, SHOW_SRUN_PORTAL_INFO, SHOW_USER_INFO
    DEBUG_MODE              = True
    SHOW_IP                 = True
    SHOW_TOKEN              = True
    SHOW_SRUN_PORTAL_INFO   = True
    SHOW_USER_INFO          = True

    from sys import argv

    if len(argv) == 1:
        help_menu()

    elif len(argv) == 2:
        if argv[1] == 'info':
            userinfo = get_status()
            try:
                print("用户名：{}".format(userinfo[0]))
                print("剩余流量：{}".format(format_flux(userinfo[1])))
                print("已用时长：{}".format(format_time(userinfo[2])))
                print("设备IP地址：{}".format(userinfo[3]))
                print("剩余金额：{}".format(userinfo[4]))
            except:
                pass

        else:
            help_menu()

    elif len(argv) == 4:
        username = argv[2]
        password = argv[3]
        try:
            init_work()
        except:
            print("请检查账号和密码的格式是否有误")

        if argv[1] == 'login':
            login()

        elif argv[1] == 'logout':
            logout()
        
        elif argv[1] == 'autologin':
            auto_login(2, 4, username, password)

    else:
        help_menu()
  
#auto_login(2, 4, username, password)
