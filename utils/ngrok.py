import requests


def get_ngrok_tunnel():
    r = requests.get("http://localhost:4040/api/tunnels")
    return r.json()["tunnels"][0]['public_url']