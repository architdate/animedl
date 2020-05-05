from urllib.parse import urlencode
from funimation.auth import api_request, login, build_proxy
from funimation.util import get_filename, PROCESS_COUNT
import sys, subprocess, json, os, string, io, pycaption, requests

API_ENDPOINT = 'https://prod-api-funimationnow.dadcdigital.com/api'

def get_episode(session, token, url, res, dubbed, output_folder, proxy = None):
    if not url.startswith('https://www.funimation.com/shows/'):
        sys.exit(1)
    url = url.split('/?')[0]
    slugs = url.split('https://www.funimation.com/shows/')[1].split('/')
    if len(slugs) == 1:
        print(f'Invalid Slug: {slugs}')
        # show, return for now
        sys.exit(1)
    show_slug, epi_slug = slugs[0], slugs[1]
    x = api_request(session, {'baseUrl': API_ENDPOINT, 'url': f'/source/catalog/episode/{show_slug}/{epi_slug}', 'token': token})
    if not x:
        print("API request failed!")
        return
    x = x['items'][0]
    snum = enum = '?'
    if 'seasonNumber' in x['parent']:
        snum = x["parent"]["seasonNumber"]
    if 'number' in x:
        enum = x['number']
    ename = f'{x["parent"]["title"]} - S{snum}E{enum} - {x["title"]}'
    print(f'[INFO] {ename}')
    media = x['media']
    tracks = []
    uncut = {'Japanese': False, 'English': False}
    for m in media:
        if m['mediaType'] == 'experience':
            if 'uncut' in m['version'].lower():
                uncut[m['language']] = True
            tracks.append({'id': m['id'], 'language': m['language'], 'version': m['version'], 'type': m['experienceType'], 'subs': get_subs(m['mediaChildren'])})
    tracks = [track for track in tracks if ((track['language'] == 'Japanese' and not dubbed) or (track['language'] == 'English' and dubbed))]
    if tracks == []: return
    for i in tracks:
        print(f'{str(tracks.index(i) + 1).zfill(2)} [{i["id"]}] {i["language"]} - {i["version"]}')
    if len(tracks) > 1:
        sel_id = tracks[int(input("Select which version you want to download: ")) - 1]
    else: sel_id = tracks[0]
    sel_id['name'] = ename
    download_episode(session, token, sel_id, res, output_folder, proxy)

def download_episode(session, token, epi, res, output_folder, proxy = None):
    x = api_request(session, {'baseUrl': API_ENDPOINT, 'url': f'/source/catalog/video/{epi["id"]}/signed', 'token': token, 'dinstid': 'Android Phone'})
    if not x:
        return
    if 'errors' in x:
        print(f'[ERROR] Error #{x["errors"][0]["code"]}: {x["errors"][0]["detail"]}')
        return
    vid_path = None
    for i in x["items"]:
        if i["videoType"] == 'm3u8':
            vid_path = i['src']
    if vid_path == None:
        return
    a = session.get(vid_path)
    playlist = parse_playlist(a.text)
    playlist = [item for item in playlist if res in item['res']]
    successful = False
    while not successful:
        print('[INFO] Available qualities:')
        for i in range(len(playlist)):
            print(f'{str(i+1).zfill(2)} Resolution: {playlist[i]["res"]} [Bandwidth: {playlist[i]["bandwidth"]}KiB/s]')
        selection = int(input("Select the stream to download: ")) - 1
        url = playlist[selection]['url']
        try:
            streamlink_call(session, url, epi, output_folder, proxy)
            break
        except:
            playlist.pop(selection)
            print("This stream is broken, please choose another one.")

def streamlink_call(session, m3u8_text, file, path = os.getcwd(), proxy = None):
    try:
        if proxy:
            streamlink_command = f'streamlink --http-proxy "{proxy["http"]}" --hls-segment-threads {PROCESS_COUNT} --force "{m3u8_text}" live -o "{path}/{get_filename(file["name"])}.ts"'
        else:
            streamlink_command = f'streamlink --hls-segment-threads {PROCESS_COUNT} --force "{m3u8_text}" live -o "{path}/{get_filename(file["name"])}.ts"'
        print(streamlink_command)
        try:
            call = subprocess.check_call(streamlink_command, shell=True)
            print(f"HERE IS THE CALL {call}")
        except subprocess.CalledProcessError:
            pass
        subs_available = True
        try:
            download_subs(session, file['subs'], path, get_filename(file["name"]))
            ffmpeg_command = f'ffmpeg -i "{path}/{get_filename(file["name"])}.ts" -i "{path}/{get_filename(file["name"])}.srt" -c copy -scodec copy "{path}/{get_filename(file["name"])}.mkv"'
        except Exception as e:
            print(f"[INFO] Exception during subs download: {e}")
            subs_available = False
            ffmpeg_command = f'ffmpeg -i "{path}/{get_filename(file["name"])}.ts" -c copy "{path}/{get_filename(file["name"])}.mkv"'
        call2 = subprocess.check_call(ffmpeg_command, shell=True)
        os.remove(f"{path}/{get_filename(file['name'])}.ts")
        if call:
            return True
        else:
            return False
    except Exception:
        return False

def parse_playlist(plist):
    l = plist.split('\n')
    playlist = []
    i = 0
    while i < len(l):
        if l[i].startswith('#EXT-X-STREAM-INF:'):
            url = l[i+1]
            res = l[i].rsplit('x', 1)[1] + 'p'
            bandwidth = int(l[i].split('BANDWIDTH=')[1].split(',')[0])//1024
            playlist.append({'url': url, 'res': res, 'bandwidth': bandwidth})
        i+=1
    return playlist

def get_subs(m):
    for i in m:
        fp = i['filePath']
        if fp.split('.')[-1] == 'dfxp': return fp
    return False

def download_subs(session, link, output_folder, name):
    x = session.get(link, headers={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0' })
    caption_set = pycaption.DFXPReader().read(x.text)
    results = pycaption.SRTWriter().write(caption_set)
    with io.open(os.path.join(output_folder, name + '.srt'), 'w', encoding='utf-8') as f:
        f.write(results)