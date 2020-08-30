from tamtambot import TamTamVoiceBot
from flask import Flask, request


app = Flask(__name__)
bot = TamTamVoiceBot()

@app.route('/', methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        bot.create_answer(request.json)
    return {"ok": True}
