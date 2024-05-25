import socket
import threading
import json

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5555

def listen_for_messages(port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(('0.0.0.0', port))
    listening_socket.listen(5)
    print(f"메시지 수신 대기 중... (포트: {port})")

    while True:
        conn, addr = listening_socket.accept()
        threading.Thread(target=handle_message, args=(conn,)).start()

def handle_message(conn):
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message:
                print(f"\n[메시지 수신] {message}")
        except:
            conn.close()
            break

def start_client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        
        id = input("아이디를 입력하세요: ")
        port = int(input("포트를 입력하세요: "))

        login_request = {
            'action': 'login',
            'id': id,
            'port': port
        }

        client_socket.send(json.dumps(login_request).encode('utf-8'))
        response = json.loads(client_socket.recv(1024).decode('utf-8'))
        online_users = response['online_users']

        print("온라인 사용자 목록:")
        for user_id, details in online_users.items():
            print(f"{user_id}: {details['ip']}:{details['port']}")

        threading.Thread(target=listen_for_messages, args=(port,)).start()

        while True:
            print("\n1. 메시지 보내기")
            print("2. 로그아웃")
            action = input("선택하세요: ")

            if action == '1':
                recipient_id = input("메시지를 보낼 사용자의 아이디를 입력하세요: ")
                message = input("메시지를 입력하세요: ")
                recipient = online_users.get(recipient_id)
                if recipient:
                    try:
                        recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        recipient_socket.connect((recipient['ip'], recipient['port']))
                        recipient_socket.send(f"{id}: {message}".encode('utf-8'))
                        recipient_socket.close()
                    except ConnectionRefusedError:
                        print(f"{recipient_id}는 현재 연결할 수 없습니다.")
                else:
                    print(f"{recipient_id}를 찾을 수 없습니다.")
            elif (action == "2"):
                break
    finally:
        logout_request = {
            'action': 'logout',
            'id': id,
            'port': port
        }
        client_socket.send(json.dumps(logout_request).encode('utf-8'))

    

if __name__ == "__main__":
    start_client()

