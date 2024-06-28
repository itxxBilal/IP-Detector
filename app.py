from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import requests
import user_agents

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')

def get_public_ip():
    response = requests.get("https://httpbin.org/ip")
    return response.json()["origin"]

def get_ip_info(ip):
    response = requests.get(f"http://ip-api.com/json/{ip}")
    return response.json()

@app.route('/')
def index():
    user_ip = get_public_ip()
    ip_info = get_ip_info(user_ip)
    ua = user_agents.parse(request.headers.get('User-Agent'))
    user_agent_info = {
        "browser": ua.browser.family,
        "platform": ua.os.family,
        "version": ua.browser.version_string,
        "device": ua.device.family
    }
    return render_template('index.html', ip=user_ip, location=ip_info, user_agent_info=user_agent_info)

@socketio.on('connect')
def handle_connect():
    user_ip = get_public_ip()
    ip_info = get_ip_info(user_ip)
    ua = user_agents.parse(request.headers.get('User-Agent'))
    user_agent_info = {
        "browser": ua.browser.family,
        "platform": ua.os.family,
        "version": ua.browser.version_string,
        "device": ua.device.family
    }
    emit('ip_info', {'ip': user_ip, 'location': ip_info, 'user_agent_info': user_agent_info})

if __name__ == '__main__':
    import os
    if 'PORT' in os.environ:  # for deployment on Vercel
        socketio.run(app, host='0.0.0.0', port=int(os.environ['PORT']))
    else:
        socketio.run(app, host='localhost', port=5000, debug=True)
