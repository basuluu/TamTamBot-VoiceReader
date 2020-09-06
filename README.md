This webhook-bot takes text from voice messages and reply it. It use WIT-AI to recognize voice to text.


### Install using Docker
1. Set your tamtam token and wit api key in settings.py
```
tamtam_token = 'Your tamtam token'
wit_api_key = 'Your wit api key'
```
2. Build and run container
```
docker build -t voice_reader .
docker run -p 5000:5000 voice_reader:latest
```