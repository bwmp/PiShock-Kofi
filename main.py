import json
import socket
import threading
from flask import Flask, jsonify, request
import requests
from pishock.zap.httpapi import PiShockAPI, ShockerPausedError
from ConfigManager import ConfigManager

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_post():
    content_type = request.headers.get("Content-Type")
    if content_type == "application/x-www-form-urlencoded":
        form_data = request.form
        data = form_data.get("data")
        if data:
            json_data = json.loads(data)

            verification_token = json_data.get("verification_token")
            if verification_token != secret:
              return jsonify({"error": "Invalid verification token"}), 400
            shop_items = json_data.get("shop_items")
            if not shop_items:
              return jsonify({"error": "Missing 'shop_items' parameter"}), 400
            for item in shop_items:
              print(item)
              if item["direct_link_code"] in items.keys():
                intensity = items[item["direct_link_code"]]["intensity"]
                duration = items[item["direct_link_code"]]["duration"]
                for shocker in shockers:
                    try:
                        shocker.shock(duration=duration, intensity=intensity)
                    except ShockerPausedError:
                        pass
            return jsonify({"message": "Received and processed form data"}), 200
        else:
            return jsonify({"error": "Missing 'data' parameter"}), 400
    else:
        print("Unsupported content type:", content_type)
        return "Unsupported Media Type", 415


def get_public_ip():
    response = requests.get("https://api.ipify.org?format=json")
    data = response.json()
    return data["ip"]


def is_port_open(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        print(f"Port {port} is open")
        return True
    except (socket.error, socket.timeout):
        print(f"Port {port} is closed or unreachable")
        return False
    finally:
        s.close()


def run_temporary_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(1)
    print(f"Temporary server listening on port {port}")
    conn = None
    try:
        conn, addr = server_socket.accept()
        print(f"Connection established from {addr}")
    finally:
        if conn:
            conn.close()
        server_socket.close()

def init():
    global share_codes, items, secret
    config = ConfigManager("config.json")
    config.load_config()
    items = config.get_items()
    share_codes = config.get_share_codes()
    secret = config.get_secret()
    username = config.get_username()
    api_key = config.get_api_key()
    api = PiShockAPI(username, api_key)
    shockers = None
    for code in share_codes:
          shocker = api.shocker(code)
          shockers = [shocker] if shockers is None else shockers + [shocker]
    print (f"Loaded {len(shockers)} shockers")
    return config, items, secret, api, shockers

config, items, secret, api, shockers = init()
print(items.keys())
port = 9183
public_ip = get_public_ip()
print(f"Public IP: {public_ip}")
server_thread = threading.Thread(target=run_temporary_server, args=(port,))
server_thread.start()
try:
    port_open = is_port_open(public_ip, port)
    if not port_open:
        print(
            f"Port {port} is not open. To open the port, google how to port forward for your internet service provider"
        )
        exit(1)
    print(f"Port {port} is open from the internet")
finally:
    server_thread.join()
print(f"Server running on http://{public_ip}:{port}")
app.run(host="0.0.0.0", port=port)
