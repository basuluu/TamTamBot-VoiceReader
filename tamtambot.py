from wit import Wit
from threading import Thread
import subprocess
import requests
import os
import settings

class TamTamVoiceBot():
    
    base_url = 'https://botapi.tamtam.chat'
    access_token = settings.tamtam_token
    wit_api_key = settings.wit_api_key
    

    def __init__(self):
        self.client = Wit('ZK3W3NFUHDO3ORWT4GYG4XUA7ODCP24Q')

    
    def send_message_by_chat_id(self, chat_id, mid, text):
        url = self.base_url + '/messages'
       
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        params = {
            'access_token': self.access_token,
            'chat_id': chat_id,
        }
        data = {
            'text': text,
            'attachments': None,
            'link': None
        }
        
        if mid:
            data['link'] = {
                'type': 'reply',
                'mid': mid
            }
        
        r = requests.post(url=url, headers=headers, params=params, json=data)
        return r.json()['message']['body']['mid']
    
    def edit_message_by_message_id(self, last_mid, mid, text):
        url = self.base_url + '/messages'
       
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        params = {
            'access_token': self.access_token,
            'message_id': last_mid,
        }
        data = {
            'text': text,
            'attachments': None,
            'link': {
                'type': 'reply',
                'mid': mid
            }
        }
        
        r = requests.put(url=url, headers=headers, params=params, json=data)
        
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
        return resp['_text']
    
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
    
    def get_voice_message_link(self, upd):
        if upd['message'].get('link', False):
            link = upd['message']['link']['message']['attachments'][0]['payload']['url']
        else:
            link = upd['message']['body']['attachments'][0]['payload']['url']
        return link
    
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
        
        link = self.get_voice_message_link(upd)
        file_name = self.get_audio_file_name(upd)
        
        self.download_voice_message(link, file_name)
        self.devide_audio_file(file_name)
        file_names = self.get_devided_audio_file_names(file_name)
        
        text = "Текст: "
        for fn in file_names:
            text += self.get_text_by_audio(fn) + ' '
            
        self.edit_message_by_message_id(last_mid, mid, text)
        
    def devide_audio_file(self, file_name):
        cmd = "/usr/bin/ffmpeg -i {fn} -f segment -segment_time 19 -c copy {ofn}_%02d.mp3".format(
            fn=file_name,
            ofn=file_name[:-4]
        )
        subprocess.run(cmd.split())

    def get_devided_audio_file_names(self, file_name):
        return sorted([fn for fn in os.listdir() if fn.startswith(file_name[:-4] + '_')])
        
    def get_message_id(self, upd):
        return upd['message']['body']['mid']
    
    def polling(self):
        while True:
            try:
                url = self.base_url + '/updates'
                params = {
                    'access_token': self.access_token
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
