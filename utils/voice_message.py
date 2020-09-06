import os
import subprocess

import requests


audio_save_dir = '/app/audio_tmp/'

def get_text_by_audio(wit_client, file_name):
    with open(audio_save_dir + file_name, 'rb') as f:
        resp = wit_client.speech(f, None, {'Content-Type': 'audio/mpeg'})
    return resp['text']

def download_voice_message(url, file_name):
    ufr = requests.get(url)
    with open(audio_save_dir + file_name, 'wb') as f:
        f.write(ufr.content)

def devide_audio_file(file_name):
    fn, fmt = file_name.split('.')
    cmd = f"/usr/bin/ffmpeg -i {audio_save_dir}{file_name} -f segment -segment_time 20 -c copy {audio_save_dir}{fn}_%02d.{fmt}"
    subprocess.call(cmd.split())
    return sorted([file_ for file_ in os.listdir(audio_save_dir) if file_.startswith(fn + '_')])

def collect_garbage(file_names):
    for fn in file_names: os.remove(audio_save_dir + fn)