from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

BASE = '/DL_CP2'

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f)

def get_user(username):
    return load_json(f"{BASE}/users/{username}.json")

def is_server_owner(username, server_id):
    info = load_json(f"{BASE}/servers/{server_id}/info.json")
    if info is None:
        return False
    return info.get('owner') == username

def is_server_member(username, server_id):
    members = load_json(f"{BASE}/servers/{server_id}/members.json") or []
    return username in members

# serve the frontend
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    path = f"{BASE}/users/{username}.json"
    if os.path.exists(path):
        return jsonify({"status": "error", "msg": "User already exists"}), 400
    save_json(path, {"username": username, "servers": []})
    return jsonify({"status": "success"})

@app.route('/user/servers/<username>', methods=['GET'])
def get_user_servers(username):
    user = get_user(username)
    if user is None:
        return jsonify({"status": "error", "msg": "User not found"}), 404
    return jsonify(user.get('servers', []))

@app.route('/server/create', methods=['POST'])
def create_server():
    data = request.get_json()
    username = data.get('username')
    server_id = data.get('server_id')
    server_name = data.get('name')
    info_path = f"{BASE}/servers/{server_id}/info.json"
    if os.path.exists(info_path):
        return jsonify({"status": "error", "msg": "Server already exists"}), 400
    save_json(info_path, {"name": server_name, "owner": username})
    save_json(f"{BASE}/servers/{server_id}/members.json", [username])
    save_json(f"{BASE}/servers/{server_id}/channels/general.json", [])
    user = get_user(username) or {"username": username, "servers": []}
    user['servers'].append(server_id)
    save_json(f"{BASE}/users/{username}.json", user)
    return jsonify({"status": "success"})

@app.route('/server/delete', methods=['POST'])
def delete_server():
    data = request.get_json()
    username = data.get('username')
    server_id = data.get('server_id')
    if not is_server_owner(username, server_id):
        return jsonify({"status": "error", "msg": "Not the owner"}), 403
    import shutil
    shutil.rmtree(f"{BASE}/servers/{server_id}", ignore_errors=True)
    user = get_user(username)
    if user and server_id in user['servers']:
        user['servers'].remove(server_id)
        save_json(f"{BASE}/users/{username}.json", user)
    return jsonify({"status": "success"})

@app.route('/server/adduser', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    server_id = data.get('server_id')
    new_user = data.get('new_user')
    if not is_server_owner(username, server_id):
        return jsonify({"status": "error", "msg": "Not the owner"}), 403
    members = load_json(f"{BASE}/servers/{server_id}/members.json") or []
    if new_user not in members:
        members.append(new_user)
        save_json(f"{BASE}/servers/{server_id}/members.json", members)
    user = get_user(new_user) or {"username": new_user, "servers": []}
    if server_id not in user['servers']:
        user['servers'].append(server_id)
        save_json(f"{BASE}/users/{new_user}.json", user)
    return jsonify({"status": "success"})

@app.route('/server/channels/<server_id>', methods=['GET'])
def get_channels(server_id):
    path = f"{BASE}/servers/{server_id}/channels"
    if not os.path.exists(path):
        return jsonify([])
    channels = [f.replace('.json', '') for f in os.listdir(path) if f.endswith('.json')]
    return jsonify(channels)

@app.route('/message/send', methods=['POST'])
def send_message():
    data = request.get_json()
    username = data.get('username')
    server_id = data.get('server_id')
    channel = data.get('channel')
    msg = data.get('msg')
    if not is_server_member(username, server_id):
        return jsonify({"status": "error", "msg": "Not a member"}), 403
    path = f"{BASE}/servers/{server_id}/channels/{channel}.json"
    if not os.path.exists(path):
        return jsonify({"status": "error", "msg": "Channel does not exist"}), 404
    messages = load_json(path) or []
    entry = {"id": username, "message": msg}
    messages.append(entry)
    save_json(path, messages)
    socketio.emit('new-message', entry, room=f"{server_id}-{channel}")
    return jsonify({"status": "success"})

@app.route('/message/get/<server_id>/<channel>', methods=['GET'])
def get_messages(server_id, channel):
    path = f"{BASE}/servers/{server_id}/channels/{channel}.json"
    messages = load_json(path)
    if messages is None:
        return jsonify([])
    return jsonify(messages)

# socketio events
@socketio.on('join')
def on_join(data):
    room = f"{data['server_id']}-{data['channel']}"
    join_room(room)

@socketio.on('leave')
def on_leave(data):
    room = f"{data['server_id']}-{data['channel']}"
    leave_room(room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)