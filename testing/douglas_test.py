#DL client.py
import requests
import threading
import time

BASE_URL = "https://dogo1017.pythonanywhere.com"

def clear():
    print("\n" * 3)

def fetch_messages(server_id, channel):
    r = requests.get(f"{BASE_URL}/message/get/{server_id}/{channel}")
    if r.status_code == 200:
        return r.json()
    return []

def fetch_channels(server_id):
    r = requests.get(f"{BASE_URL}/server/channels/{server_id}")
    if r.status_code == 200:
        return r.json()
    return []

def fetch_user_servers(username):
    r = requests.get(f"{BASE_URL}/user/servers/{username}")
    if r.status_code == 200:
        return r.json()
    return []

def print_messages(messages):
    if not messages:
        print("  (no messages yet)")
    for m in messages:
        print(f"  {m['id']}: {m['message']}")

def print_servers(servers):
    print("\nYour servers:")
    if not servers:
        print("  (none)")
    for i, s in enumerate(servers):
        print(f"  {i+1}. {s}")

def notification_listener(username, servers, current_server, current_channel, last_counts):
    while True:
        time.sleep(5)
        for server_id in servers:
            channels = fetch_channels(server_id)
            for channel in channels:
                key = f"{server_id}/{channel}"
                msgs = fetch_messages(server_id, channel)
                count = len(msgs)
                if key in last_counts and count > last_counts[key]:
                    if server_id != current_server[0] or channel != current_channel[0]:
                        latest = msgs[-1]
                        print(f"\n  [new message] {server_id} / #{channel} - {latest['id']}: {latest['message']}")
                last_counts[key] = count

def chat_view(username, server_id, channel):
    last_count = 0
    current_server = [server_id]
    current_channel = [channel]

    print(f"\n--- {server_id} / #{channel} ---")
    print("type message to send, 'back' to go back\n")

    messages = fetch_messages(server_id, channel)
    print_messages(messages)
    last_count = len(messages)

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == 'back':
            break

        if user_input == '':
            messages = fetch_messages(server_id, channel)
            new = messages[last_count:]
            for m in new:
                print(f"  {m['id']}: {m['message']}")
            last_count = len(messages)
            continue

        r = requests.post(f"{BASE_URL}/message/send", json={
            "username": username,
            "server_id": server_id,
            "channel": channel,
            "msg": user_input
        })
        if r.status_code == 200:
            print(f"  {username}: {user_input}")
            last_count += 1
        else:
            print(f"  error sending: {r.text}")

def server_view(username, server_id):
    while True:
        channels = fetch_channels(server_id)
        if not channels:
            print("  no channels found")
            return

        print(f"\n--- {server_id} ---")
        print("channels:")
        for i, c in enumerate(channels):
            print(f"  {i+1}. #{c}")
        print("\n  'back' to go back")

        choice = input("> ").strip().lower()

        if choice == 'back':
            break

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(channels):
                chat_view(username, server_id, channels[idx])
            else:
                print("  invalid choice")
        else:
            print("  invalid choice")

def main_menu(username):
    servers = fetch_user_servers(username)
    last_counts = {}
    current_server = [None]
    current_channel = [None]

    t = threading.Thread(
        target=notification_listener,
        args=(username, servers, current_server, current_channel, last_counts),
        daemon=True
    )
    t.start()

    while True:
        servers = fetch_user_servers(username)
        print_servers(servers)
        print("\n  c - create server")
        print("  d - delete server")
        print("  a - add user to server")
        print("  q - quit")
        print("\nenter server number or command")

        choice = input("> ").strip().lower()

        if choice == 'q':
            break

        elif choice == 'c':
            server_id = input("  server id: ").strip()
            name = input("  server name: ").strip()
            r = requests.post(f"{BASE_URL}/server/create", json={
                "username": username,
                "server_id": server_id,
                "name": name
            })
            print(f"  {r.json().get('status', 'error')}")
            servers = fetch_user_servers(username)

        elif choice == 'd':
            server_id = input("  server id: ").strip()
            if server_id not in servers:
                print("  you are not in that server")
                continue
            r = requests.post(f"{BASE_URL}/server/delete", json={
                "username": username,
                "server_id": server_id
            })
            print(f"  {r.json().get('msg', r.json().get('status'))}")

        elif choice == 'a':
            server_id = input("  server id: ").strip()
            if server_id not in servers:
                print("  you are not in that server")
                continue
            new_user = input("  username to add: ").strip()
            r = requests.post(f"{BASE_URL}/server/adduser", json={
                "username": username,
                "server_id": server_id,
                "new_user": new_user
            })
            print(f"  {r.json().get('msg', r.json().get('status'))}")

        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                server_view(username, servers[idx])
            else:
                print("  invalid server number")

        else:
            print("  invalid command")

print("=== chat client ===")
username = input("username: ").strip()

r = requests.get(f"{BASE_URL}/user/servers/{username}")
if r.status_code == 404:
    create = input("  user not found. create account? (y/n): ").strip().lower()
    if create == 'y':
        requests.post(f"{BASE_URL}/user/create", json={"username": username})
    else:
        exit()

main_menu(username)