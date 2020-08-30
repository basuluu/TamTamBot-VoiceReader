import os
import subprocess
from threading import Thread

import requests
from wit import Wit

import settings

"""
    TODO: Refactor!
    TODO: Replace WIT
    TODO: Stop spam ffmpeg!
    TODO: Replace threads -> Async!
    TODO: Web hook! KILL POLLING!
"""

class TamTamVoiceBot():
    
    API_URL = 'https://botapi.tamtam.chat'

    tam_api_key = settings.tamtam_token
    wit_api_key = settings.wit_api_key

    MSG_ONLY_VOICE = "Я умею работать только с голосовыми сообщениям :("
    MSG_START_RECOGNIZE = "Начинаю распознавание!"

    def __init__(self):
        self.client = Wit(self.wit_api_key)

    def send_message_by_chat_id(self, chat_id, msg_id, text):
        query_params = {
            'url': self.API_URL + '/messages',
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            },
            'params': {
                'access_token': self.tam_api_key, 
                'chat_id': chat_id
            },
            'json': {
                'text': text, 
                'attachments': None, 
                'link': {'type': 'reply', 'mid': msg_id} if msg_id else None
            },
        }
        r = requests.post(**query_params)
        return r.json()['message']['body']['mid']

    def edit_message_by_message_id(self, last_msg_id, msg_id, text):
        query_params = {
            'url': self.API_URL + '/messages',
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            },
            'params': {
                'access_token': self.tam_api_key,
                'message_id': last_msg_id,
            },
            'json': {
                'text': text,
                'attachments': None,
                'link': {
                    'type': 'reply',
                    'mid': msg_id
                }
            }
        }    
        r = requests.put(**query_params)
        
    def download_voice_message(self, url, file_name):
        ufr = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(ufr.content)
            
    def get_text_by_audio(self, audio_file_name):
        with open(audio_file_name, 'rb') as f:
            resp = self.client.speech(f, None, {'Content-Type': 'audio/mpeg'})
        return resp['text']
    
    def get_voice_message_url(self, upd):
        try:
            if upd['message'].get('link', False):
                msg = upd['message']['link']['message']
            else:
                msg = upd['message']['body']
            return msg['attachments'][0]['payload']['url']
        except KeyError:
            return None
    
    def get_message_id(self, upd):
        return upd['message']['body']['mid']

    def get_chat_id(self, upd):
        return upd['message']['recipient']['chat_id']
    
    def get_audio_file_name(self, upd):
        return '%s.mp3' % upd['message']['body']['seq']
        
    def devide_audio_file(self, file_name):
        fn, fmt = file_name.split('.')
        cmd = (
            f"/usr/bin/ffmpeg -i {file_name} -f segment -segment_time 19 -c copy {fn}_%02d.{fmt}"
        )
        subprocess.call(cmd.split())
        return sorted([file_ for file_ in os.listdir() if file_.startswith(fn + '_')])        
    
    def create_answer(self, upd):        
        msg_id  = self.get_message_id(upd)
        chat_id = self.get_chat_id(upd)
        
        voice_message_url = self.get_voice_message_url(upd)
        if not voice_message_url: 
            return self.send_message_by_chat_id(chat_id, msg_id, self.MSG_ONLY_VOICE)

        last_msg_id = self.send_message_by_chat_id(chat_id, msg_id, self.MSG_START_RECOGNIZE)
        
        file_name = self.get_audio_file_name(upd)
        self.download_voice_message(voice_message_url, file_name)
        file_names = self.devide_audio_file(file_name)
        
        text = "Текст:" + ' '.join([self.get_text_by_audio(fn) for fn in file_names])
        self.edit_message_by_message_id(last_msg_id, msg_id, text)

        [os.remove(fn) for fn in file_names + [file_name]]

    def polling(self):
        while True:
            try:
                query_params = {
                    'url': self.API_URL + '/updates',
                    'params': {
                        'access_token': self.tam_api_key
                    }
                }

                r = requests.get(**query_params)
                updates = r.json()['updates']
                if not updates:
                    continue

                for upd in updates:
                    th = Thread(target=self.create_answer, args=(upd,))
                    th.start()
            except KeyboardInterrupt:
                break
                

if __name__ == "__main__":
    bot = TamTamVoiceBot()
    bot.polling()
