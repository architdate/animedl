import requests, json, sys

BASE_URL = 'https://nordvpn.com/api/server'

list_serv = requests.get(BASE_URL).json()
usa_proxies = [serv for serv in list_serv if serv['flag'] == 'US' and {'name':'P2P'} in serv['categories']]
print(f'{len(usa_proxies)} valid USA proxies found!')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <nordusername> <nordpassword>')
        sys.exit(1)
    proxies = []
    for proxy in usa_proxies:
        proxy_conf = {
            "protocol": "http",
            "host": proxy['domain'],
            "port": 80,
            "username": sys.argv[1],
            "password": sys.argv[2]
        }
        proxies.append(proxy_conf)
    print('Adding proxies to proxy.json')
    with open('proxy.json', 'w') as f:
        f.write(json.dumps(proxies, indent=4))