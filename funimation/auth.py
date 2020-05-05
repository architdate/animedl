import random, json
from requests import session
from urllib.parse import urlencode

API_ENDPOINT = 'https://prod-api-funimationnow.dadcdigital.com/api'

def login(username, password, proxy = None):
    s = session()
    s.trust_env = False
    body = {'username': username, 'password': password}
    url = API_ENDPOINT + '/auth/login/'
    if proxy:
        s.proxies = proxy
    r = s.post(url, data=body).json()
    if 'token' in r:
        return s, r['token']
    return None, None

def build_proxy(proxy_dict):
    rand_proxy = random.choice(proxy_dict)
    if rand_proxy['protocol'] == 'http':
        proxy_url = f'http://{rand_proxy["username"]}:{rand_proxy["password"]}@{rand_proxy["host"]}:{rand_proxy["port"]}'
        return {'https': proxy_url, 'http': proxy_url}
    else:
        return None

def api_request(s, args):
    url = args['url']
    headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0' }
    if 'baseUrl' in args:
        url = args['baseUrl'] + args['url']
    if 'qs' in args:
        url += '?' + urlencode(args['qs'])
    if 'dinstid' in args:
        headers['devicetype'] = args['dinstid']
    if 'token' in args:
        token = args['token']
        headers['Authorization'] = f'Token {token}'
    r = s.get(url, headers=headers)
    try:
        x = r.json()
        return x
    except:
        return None