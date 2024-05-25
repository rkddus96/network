import socket
import threading
import json

ONLINE_USERS_FILE = 'online_users.json'

def load_online_users():
    try:
        with open(ONLINE_USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_online_users(users):
    with open(ONLINE_USERS_FILE, 'w') as file:
        json.dump(users, file)



def handle_client(client_socket, client_address):
    online_users = load_online_users()
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                request = json.loads(data)
                if request['action'] == 'login':
                    online_users[request['id']] = {
                        'ip': client_address[0],
                        'port': request['port']
                    }
                    save_online_users(online_users)
                    client_socket.send(json.dumps({'online_users': online_users}).encode('utf-8'))
                elif request['action'] == 'logout':
                    online_users.pop(request['id'], None)
                    save_online_users(online_users)
                    client_socket.send('로그아웃 완료')
                    break
        except:
            break
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print('로그인 서버가 포트 5555에서 시작되었습니다.')

    while True:
        client_socket, client_address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
