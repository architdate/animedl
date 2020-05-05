import requests, json

def get_subs(page):
    metadata = get_metadata(page)
    return metadata['subtitles']

def get_metadata(page):
    meta = page.text.split('vilos.config.media = ')[1].split(';\n\n')[0]
    return json.loads(meta)