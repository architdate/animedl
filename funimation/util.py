import os
import re
import requests
import sys
import subprocess
import string
from multiprocessing import Pool
# from Crypto.Cipher import AES

PROCESS_COUNT = 5

## LEGACY METHOD
'''
def decrypt(data, key, iv):
    """Decrypt using AES CBC"""
    decryptor = AES.new(key, AES.MODE_CBC, iv=iv)
    return decryptor.decrypt(data)

def get_binary(session, url):
    """Get binary data from URL"""
    a = session.get(url, stream=True)
    return a.content

def download_legacy(url, epi_name, output_folder, session, skip_ad=True):
    """Main"""
    print(url)
    base = url.rsplit('/', 1)[0]
    a = session.get(url)
    data = a.text
    # make output folder
    os.makedirs(output_folder, exist_ok=True)
    # download and decrypt chunks
    parts = []
    for part_id, sub_data in enumerate(data.split('#UPLYNK-SEGMENT:')):
        # skip ad
        if skip_ad:
            if re.findall('#UPLYNK-SEGMENT:.*,.*,ad', '#UPLYNK-SEGMENT:' + sub_data):
                continue
        # get key, iv and data
        chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)\s.*\s(.*)', sub_data)
        arglist = ([chunk, session, base, output_folder] for chunk in chunks)
        try:
            pool = Pool(PROCESS_COUNT)
            parts = pool.map(process_chunk, arglist)
        except ImportError:
            # Android devices
            for arg in arglist:
                x = process_chunk(arg)
                parts.append(x)
    if os.path.exists(os.path.join(output_folder, epi_name + '.ts')):
        os.remove(os.path.join(output_folder, epi_name + '.ts'))
    with open(os.path.join(output_folder, get_filename(epi_name) + '.ts'), 'ab') as f:
        for i in parts:
            with open(i, 'rb') as f2:
                f.write(f2.read())
    for i in parts:
        os.remove(i)
    ffmpeg_command = f'ffmpeg -i "{output_folder}/{get_filename(epi_name)}.ts" -c copy "{output_folder}/{get_filename(epi_name)}.mkv"'
    call = subprocess.check_call(ffmpeg_command, shell=True)
    if call:
        return True
    else:
        return False

def process_chunk(args):
    key_url = args[0][0]
    iv_val = args[0][1][2:]
    data_url = args[0][2]
    file_name = os.path.basename(data_url).split('?')[0]
    print('Processing "%s"' % file_name)
    # download key and data
    key = get_binary(args[1], args[2] + '/' + key_url)
    enc_data = get_binary(args[1], args[2] + '/' + data_url)
    iv = bytearray.fromhex(iv_val)
    # save decrypted data to file
    out_file = os.path.join(args[3], '%s' % file_name)
    with open(out_file, 'wb') as f:
        dec_data = decrypt(enc_data, key, iv)
        f.write(dec_data)
        return out_file
'''

def get_filename(name):
    try:
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in name if c in valid_chars)
    except:
        return "Episode Name Not Found"