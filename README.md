This polling-bot takes text from voice messages and reply it. It use wit AI to recognize voice to text

### Install it!

1. `Pip install -r requirement.txt`
2. Set settings file. 
3. Run localhost tunnel -> `./ngrok http 5000`
4. Run flask
```
export FLASK_APP=app.py
python -m flask run
```