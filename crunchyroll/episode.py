import re, requests, subprocess, os, string, json, time, sys
from multiprocessing import Pool
import crunchyroll.subtitles as subtitles
import crunchyroll.search as search

PROCESS_COUNT = 5

def log(text, isjson=False, filename='log'):
    if isjson:
        with open(f'{filename}.json', 'w') as f:
            f.write(json.dumps(text, indent=4))
    else:
        with open(f'{filename}.txt', 'w') as f:
            f.write(text)

def save(url, name, path = None):
    if url == None or name == None:
        return
    if path == None:
        path = os.getcwd()
    r = requests.get(url)
    with open(os.path.join(path, name), 'wb') as f:
        f.write(r.content)

def download_episode(resolution, url, path, session = None):
    page = session.get(url)
    res, metadata = grab_metadata(resolution, url)
    metadata= session.get(metadata).text
    if res != None and metadata != None:
        log(str(metadata.encode('utf-8')))
        fname = get_filename(metadata.split('<episode_number>')[-1].split('</episode_number>')[0].zfill(2) + ' - ' + metadata.split('<episode_title>')[-1].split('</episode_title>')[0])
        try:
            m3u8_file_link = str(re.search(r'<file>(.*?)</file>', metadata).group(1)).replace("&amp;", "&")
        except:
            log(str(metadata.encode('utf-8')), filename='m3u8exception')
        subs = subtitles.get_subs(page)
        subs_url = None
        for s in subs:
            if s['language'] == 'enUS':
                subs_url = s['url']
        if subs_url != None:
            save(subs_url, fname + '.ass')
        stream = get_stream(m3u8_file_link, res, session)
        print(f"Downloading {fname}...")
        ffmpeg_call(stream, fname, path)
        if os.path.exists(fname + '.ass'):
            os.remove(fname + '.ass')
        return fname
    else:
        return "Download failed"

def download_show(resolution, url, path, session = None, dubs = False):
    dubbed, subbed = search.get_episodes_from_show(session, url)
    if dubs and dubbed != []:
        episode_list = dubbed
    elif not dubs and subbed != []:
        episode_list = subbed
    else:
        print("Did not find any available episodes to download. Make sure the show is available in your region, or use a proxy")
        sys.exit(1)
    try:
        arglist = ((resolution, epi, path, session) for epi in episode_list)
        p = Pool(PROCESS_COUNT)
        p.map(download_helper, arglist)
    except ImportError:
        # Multiprocessing not supported, example: Android Devices
        for epi in episode_list:
            download_episode(resolution, epi, path, session)

def download_helper(args):
    a = download_episode(*args)
    print(f'{a} Downloaded!')

def get_stream(m3u8, res, session=None):
    m3u8 = session.get(m3u8).text.split('\n')
    for i in range(len(m3u8) - 1):
        if res in m3u8[i]:
            return m3u8[i+1]
    return None

def ffmpeg_call(m3u8_text, file_name, path = os.getcwd()):
    try:
        if os.path.exists(file_name + '.ass'):
            ffmpeg_command = f'ffmpeg -i "{m3u8_text}" -i "{file_name}.ass" -c copy -bsf:a aac_adtstoasc -scodec copy "{path}/{file_name}.mkv"'
        else:
            ffmpeg_command = f'ffmpeg -i "{m3u8_text}" -c copy -bsf:a aac_adtstoasc "{path}/{file_name}.mkv"'
        call = subprocess.check_call(ffmpeg_command, shell=True)
        if call:
            return True
        else:
            return False
    except Exception:
        return False

def mkvmerge_call(filename, path = os.getcwd()):
    try:
        mkvmerge_command = f'mkvmerge -o "{path}/{filename}.mkv" "{filename}.mkv" --language 0:eng --track-name 0:CrunchyrollEnglish "{filename}.ass"'
        call = subprocess.check_call(mkvmerge_command, shell=True)
        if call:
            return True
        else:
            return False
    except Exception:
        return False

def get_filename(name):
    try:
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in name if c in valid_chars)
    except:
        return "Episode Name Not Found"

def grab_metadata(resolution, url):
    res_val = None
    video_id = url.rsplit('-',1)[1].replace('/','')
    mapping = {'1920x1080': {'alias':['1080p', '1080', 'fhd', 'best'], 'vf': 108, 'vq': 80}, 
                '1280x720': {'alias':['720p', '720', 'hd'], 'vf': 106, 'vq': 62},
                '640x480': {'alias':['640', '640x480'], 'vf': 103, 'vq': 61},
                '848x480': {'alias':['480p', '480', 'sd'], 'vf': 106, 'vq': 61},
                '480x360': {'alias':['480x360'], 'vf': 106, 'vq': 61},
                '640x360': {'alias':['360p', '360'], 'vf': 106, 'vq': 60},
                '428x240': {'alias':['240p', '240'], 'vf': 106, 'vq': 60},}
    key, val = None, None
    for k, v in mapping.items():
        if resolution in v['alias']:
            key, val = k, v
    if key == None:
        return None, None
    info_url = f"http://www.crunchyroll.com/xml/?req=RpcApiVideoPlayer_GetStandardConfig&media_id={video_id}&video_format={val['vf']}&video_quality={val['vq']}&current_page={url}"
    return key, info_url