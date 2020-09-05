This polling-bot takes text from voice messages and reply it. It use wit AI to recognize voice to text

### Install it!

1. `pip3 install -r requirements.txt`
2. Set settings file. 
3. Run localhost tunnel -> `./ngrok http 5000`
4. Run flask
```
export FLASK_APP=app.py
python -m flask run
```

### Using Docker
```docker build -t voice_reader .
docker run -p 5000:5000 voice_reader:latest```