from crunchyroll import auth as crunchyroll_auth
from crunchyroll import episode as crunchyroll_episode
from crunchyroll import search as crunchyroll_search
from funimation import auth as funimation_auth
from funimation import episode as funimation_episode
import os, requests, json, sys, getopt

def create_crunchyroll_session(username, password, useproxy = True):
    s = requests.session()
    max_retries = 10
    if os.path.exists('proxy.json') and useproxy:
        with open('proxy.json', 'r') as f:
            proxylist = json.load(f)
        for i in range(max_retries):
            proxy = crunchyroll_auth.build_proxy(proxylist)
            try:
                s = crunchyroll_auth.login(username, password, proxy)
            except Exception as e: # Proxy Error
                print(f'Try {i+1}/{max_retries}: Failed (Proxy Error) {e}')
                continue
            if s != None:
                break
            print(f'Try {i+1}/{max_retries}: Failed')
    else:
        proxy = None
        s = crunchyroll_auth.login(username,password, proxy)
    return s

def process_crunchyroll(url, res, path, useproxy = True, show = False, dubbed = False):
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        if 'crunchyroll_username' in config.keys():
            username = config['crunchyroll_username']
            password = config['crunchyroll_password']
        else:
            config['crunchyroll_username'] = username = input('[*] Crunchyroll Username: ')
            config['crunchyroll_password'] = password = input('[*] Crunchyroll Password: ')
            with open('config.json', 'w') as f:
                f.write(json.dumps(config, indent=4))
    else:
        username = input('[*] Crunchyroll Username: ')
        password = input('[*] Crunchyroll Password: ')
        with open('config.json', 'w') as f:
            f.write(json.dumps({'crunchyroll_username': username, 'crunchyroll_password': password}, indent=4))

    s = create_crunchyroll_session(username, password, useproxy)
    if not show:
        crunchyroll_episode.download_episode(res, url, path, s)
    else:
        crunchyroll_episode.download_show(res, url, path, s, dubbed)

def process_funimation(url, res, path, useproxy = True, show = False, dubbed = True):
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        if 'funimation_username' in config.keys():
            username = config['funimation_username']
            password = config['funimation_password']
        else:
            config['funimation_username'] = username = input('[*] Funimation Username: ')
            config['funimation_password'] = password = input('[*] Funimation Password: ')
            with open('config.json', 'w') as f:
                f.write(json.dumps(config, indent=4))
    else:
        username = input('[*] Funimation Username: ')
        password = input('[*] Funimation Password: ')
        with open('config.json', 'w') as f:
            f.write(json.dumps({'funimation_username': username, 'funimation_password': password}, indent=4))

    proxy = None
    if os.path.exists('proxy.json') and useproxy:
        with open('proxy.json', 'r') as f:
            proxy_dict = json.load(f)
        proxy = funimation_auth.build_proxy(proxy_dict)
    s, token = funimation_auth.login(username, password, proxy)
    if s == None or token == None:
        print("Invalid credentials")
        sys.exit(1)
    if not show:
        funimation_episode.get_episode(s, token, url, res, dubbed, path, proxy)
    else:
        print("Not implemented yet")

if __name__ == "__main__":
    mode = None
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} --<mode> <url> <res>")
        sys.exit(1)
    else:
        mode = sys.argv[1]
        url = sys.argv[2]
        res = sys.argv[3]
        path = os.getcwd()
    if "--path" in sys.argv:
        path = sys.argv[sys.argv.index('--path') + 1]
    if mode == "--cr" or mode == "--crunchyroll":
        process_crunchyroll(url, res, path, '--noproxy' not in sys.argv, '--show' in sys.argv, '--dubbed' in sys.argv)
    if mode == "--funi" or mode == "--funimation":
        process_funimation(url, res, path, '--noproxy' not in sys.argv, '--show' in sys.argv, '--dubbed' in sys.argv)