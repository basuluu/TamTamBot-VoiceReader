from wit import Wit
from threading import Thread
import subprocess
import requests
import os
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

    def __init__(self):
        self.client = Wit(self.wit_api_key)

    def send_message_by_chat_id(self, chat_id, mid, text):
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
                'link': {'type': 'reply', 'mid': mid} if mid else None
            },
        }
        r = requests.post(**query_params)
        return r.json()['message']['body']['mid']
    
    def edit_message_by_message_id(self, last_mid, mid, text):
        query_params = {
            'url': self.API_URL + '/messages',
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            },
            'params': {
                'access_token': self.tam_api_key,
                'message_id': last_mid,
            },
            'json': {
                'text': text,
                'attachments': None,
                'link': {
                    'type': 'reply',
                    'mid': mid
                }
            }
        }    
        r = requests.put(**query_params)
        
    def send_error_message(self, chat_id, mid):
        text = "Я умею работать только с голосовыми сообщениями :("
        self.send_message_by_chat_id(chat_id, mid, text)
        
    def download_voice_message(self, link, file_name):
        ufr = requests.get(link)
        with open(file_name, 'wb') as f:
            f.write(ufr.content)
            
    def get_text_by_audio(self, audio_file_name):
        with open(audio_file_name, 'rb') as f:
            resp = self.client.speech(f, None, {'Content-Type': 'audio/mpeg'})
        return resp['text']
    
    def is_voice_message(self, upd):
        if upd['message'].get('link', False):
            
            if not upd['message']['link']['message'].get('attachments', False):
                return False
            
            if upd['message']['link']['message']['attachments'][0]['type'] == 'audio':
                return True
                        
        if not upd['message']['body'].get('attachments', False):
            return False

        if upd['message']['body']['attachments'][0]['type'] == 'audio':
            return True
        return False
    
    def get_voice_message_url(self, upd):
        if upd['message'].get('link', False):
            msg = upd['message']['link']['message']
        else:
            msg = upd['message']['body']
        return msg['attachments'][0]['payload']['url']
    
    def get_chat_id(self, upd):
        return upd['message']['recipient']['chat_id']
    
    def get_audio_file_name(self, upd):
        return '%s.mp3' % upd['message']['body']['seq']
    
    def create_answer(self, upd):
        # Добавить reply сообщения
        
        chat_id = self.get_chat_id(upd)
        mid = self.get_message_id(upd)
        
        if not self.is_voice_message(upd):
            return self.send_error_message(chat_id, mid)

        text = "Начинаю распознавание!"  
        last_mid = self.send_message_by_chat_id(chat_id, mid, text)
        
        voice_message_url = self.get_voice_message_url(upd)
        file_name = self.get_audio_file_name(upd)
        
        self.download_voice_message(voice_message_url, file_name)
        self.devide_audio_file(file_name)
        file_names = self.get_devided_audio_file_names(file_name)
        
        text = "Текст: "
        for fn in file_names:
            text += self.get_text_by_audio(fn) + ' '
            
        self.edit_message_by_message_id(last_mid, mid, text)
        
    def devide_audio_file(self, file_name):
        fn, fmt = file_name.split('.')
        cmd = (
            f"/usr/bin/ffmpeg -i {file_name} -f segment -segment_time 19 -c copy {fn}_%02d.{fmt}; "
            f"rm {file_name}"
        )
        subprocess.run(cmd.split())

    def get_devided_audio_file_names(self, file_name):
        return sorted([fn for fn in os.listdir() if fn.startswith(file_name[:-4] + '_')])
        
    def get_message_id(self, upd):
        return upd['message']['body']['mid']
    
    def polling(self):
        while True:
            try:
                url = self.API_URL + '/updates'
                params = {
                    'access_token': self.tam_api_key
                }
                r = requests.get(url=url, params=params)
                updates = r.json()['updates']
                if not updates:
                    continue

                for upd in updates:
                    th = Thread(target=self.create_answer, args=(upd,))
                    th.start()
            except:
                continue
                

if __name__ == "__main__":
    bot = TamTamVoiceBot()
    bot.polling()
