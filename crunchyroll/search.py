import requests, json
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from bs4 import BeautifulSoup

SERIES_SEARCH = 'https://www.crunchyroll.com/ajax/?req=RpcApiSearch_GetSearchCandidates'
SEASON_SEARCH = 'https://api.crunchyroll.com/list_collections.0.json'
EPISODE_SEARCH = 'https://www.crunchyroll.com/syndication/feed?type=episodes&lang=enUS&id='

def log(text, isjson=False):
    if isjson:
        with open('log.json', 'w') as f:
            f.write(json.dumps(text, indent=4))
    else:
        with open('log.txt', 'w') as f:
            f.write(text)

def search_crunchyroll(session, term):
    all_series = json.loads('{' + (session.get(SERIES_SEARCH).text.rsplit('}', 1)[0] + '}').split('{', 1)[1])
    search_results = [f'[{i["id"]}] {i["name"]}' for i in all_series['data'] if term.lower() in i['name'].lower()]
    return search_results

def get_seasons(session, series_id):
    session_id = session.cookies['session_id']
    search_params = {'series_id': series_id, 'fields': 'collection.collection_id,collection.name', 
    'locale': 'enUS', 'session_id': session_id, 'limit': '5000', 'offset': '0'} 
    results = requests.get(f'{SEASON_SEARCH}?{urlencode(search_params)}').json()
    if results['error'] != False:
        return None
    else:
        return results['data']

def get_episodes(session, series_id):
    url = EPISODE_SEARCH + str(series_id)
    episodes = []
    try:
        r = requests.get(url, timeout=20).text
    except requests.Timeout:
        print("Request Timed out! Crunchyroll is being weird!")
        return None
    root = ET.fromstring(r)
    channel = root.find('channel')
    for item in channel.findall('item'):
        episodes.append((item.find('title').text, item.find('guid').text))
    return episodes

def get_episodes_from_show(session, show_link):
    dubbed = []
    subbed = []
    if not session:
        session = requests.session()
    bsl = BeautifulSoup(session.get(show_link).text.encode('utf-8'), 'html.parser')
    epis = bsl.find_all('a', {'class': 'portrait-element block-link titlefix episode'})
    for epi in epis:
        link = show_link + '/' + epi['href'].split('/')[-1]
        name = epi['title']
        if "(Dub)" in name:
            dubbed.append(link)
        else:
            subbed.append(link)
    return dubbed, subbed


if __name__ == "__main__":
    test_url = 'https://www.crunchyroll.com/syndication/feed?type=episodes&lang=enUS&id=20461'
    r = requests.get(test_url).text
    root = ET.fromstring(r)
    channel = root.find('channel')