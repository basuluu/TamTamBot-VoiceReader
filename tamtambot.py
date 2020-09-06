import requests
from wit import Wit

import settings
from utils.voice_message import get_text_by_audio, download_voice_message, devide_audio_file, collect_garbage


class TamTamVoiceBot():
    
    API_URL = 'https://botapi.tamtam.chat'

    webhook_url = settings.ngrok_url
    tam_api_key = settings.tamtam_token
    wit_api_key = settings.wit_api_key

    MSG_ONLY_VOICE = "Я умею работать только с голосовыми сообщениям :("
    MSG_START_RECOGNIZE = "Начинаю распознавание!"

    def __init__(self):
        self.client = Wit(self.wit_api_key)
        self.set_webhook()

    def set_webhook(self):
        query_params = {
            'url': self.API_URL + '/subscriptions',
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            },
            'params': {
                'access_token': self.tam_api_key, 
            },
            'json': {
                'url': self.webhook_url,
            }
        }
        r = requests.post(**query_params)

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
    
    def create_answer(self, upd):        
        msg_id  = self.get_message_id(upd)
        chat_id = self.get_chat_id(upd)
        
        voice_message_url = self.get_voice_message_url(upd)
        if not voice_message_url: 
            return self.send_message_by_chat_id(chat_id, msg_id, self.MSG_ONLY_VOICE)

        last_msg_id = self.send_message_by_chat_id(chat_id, msg_id, self.MSG_START_RECOGNIZE)
        
        file_name = self.get_audio_file_name(upd)
        download_voice_message(voice_message_url, file_name)
        file_names = devide_audio_file(file_name)
        
        # TODO: Передаю туда сейчас название файла, а надо путь
        text = "Текст:" + ' '.join([get_text_by_audio(self.client, fn) for fn in file_names])
        self.edit_message_by_message_id(last_msg_id, msg_id, text)

        collect_garbage(file_names + [file_name])
                

if __name__ == "__main__":
    bot = TamTamVoiceBot()