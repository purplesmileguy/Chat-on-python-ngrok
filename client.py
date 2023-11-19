import socket
import threading

def receive_messages(client_socket, username):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')
            print(message)
        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")
            break

def send_messages(client_socket, username):
    while True:
        try:
            print("", end="")  # Пустой print для перехода к новой строке
            message = input()
            client_socket.send(f"{username}: {message}".encode('utf-8'))
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            break

def main():
    host, port = input("Введите хост и порт для подключения (host:port): ").split(':')
    port = int(port)

    username = input("Введите ваш ник: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        client_socket.send(username.encode('utf-8'))
    except Exception as e:
        print(f"Ошибка при отправке ника: {e}")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, username))
    send_thread = threading.Thread(target=send_messages, args=(client_socket, username))

    receive_thread.start()
    send_thread.start()

if __name__ == "__main__":
    main()
