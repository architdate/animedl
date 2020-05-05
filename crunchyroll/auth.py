import requests, json, random

BASE_WEBSITE = 'https://www.crunchyroll.com'

def log(text, json=False):
    if json:
        with open('log.json', 'w') as f:
            f.write(json.dumps(text, indent=4))
    else:
        with open('log.txt', 'w') as f:
            f.write(text)

def login(username, password, proxy = None):
    headers = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referer': 'https://www.crunchyroll.com/login',
        'origin': 'https://www.crunchyroll.com',
        'upgrade-insecure-requests': '1'
    }
    s = requests.session()
    s.trust_env = False
    if proxy:
        s.proxies = proxy
    login_page = s.get(BASE_WEBSITE + '/login', headers = headers)
    if login_page.status_code == 200:
        # Reached the website
        token = login_page.text.split('login_form[_token]')[1].split('value="')[1].split('"')[0]
        login_attempt = s.post(BASE_WEBSITE + '/login', data = {'login_form[name]' : username, 'login_form[password]' : password, 
                'login_form[redirect_url]' : '/', 'login_form[_token]' : token}, headers = headers)
        if 'href="/logout"' in login_attempt.text:
            return s
        elif 'href="/logout"' in s.get(BASE_WEBSITE, cookies=login_attempt.cookies, headers = {'User-Agent': headers['user-agent'], 'Accept-Encoding': 'gzip, deflate'}).text:
            return s
        log(str(login_attempt.text.encode('utf-8')))
        return None
    else:
        print("Could not reach the login site. Crunchyroll may be down right now.")
        return None

def build_proxy(proxy_dict):
    rand_proxy = random.choice(proxy_dict)
    if rand_proxy['protocol'] == 'http':
        proxy_url = f'http://{rand_proxy["username"]}:{rand_proxy["password"]}@{rand_proxy["host"]}:{rand_proxy["port"]}'
        return {'https': proxy_url, 'http': proxy_url}
    else:
        return None