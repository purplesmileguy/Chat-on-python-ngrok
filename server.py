import socket
import threading
import gzip
from io import BytesIO
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

def handle_client(client_socket, clients, addresses):
    try:
        # Первое сообщение от клиента должно быть никнеймом
        username = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.GREEN}{addresses[clients.index(client_socket)]} присоединился как {username}.")
    except Exception as e:
        print(f"Ошибка при получении ника от клиента: {e}")
        client_socket.close()
        return

    first_message = True  # Флаг для определения первого сообщения от клиента

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')
            sender_address = addresses[clients.index(client_socket)]

            # Проверка флага для вывода сообщения о присоединении
            if first_message:
                first_message = False
            else:
                # Проверка, содержится ли никнейм в сообщении
                if username not in message:
                    print(f"{Fore.GREEN}Получено сообщение от {sender_address}: {username}: {message}")
                else:
                    print(f"{Fore.GREEN}Получено сообщение от {sender_address}: {message}")

                # Пересылка сообщения другим клиентам, включая никнейм отправителя
                for other_client, other_address in zip(clients, addresses):
                    if other_client != client_socket:
                        try:
                            other_client.send(f"{username}: {message}".encode('utf-8'))
                        except Exception as e:
                            print(f"Ошибка отправки сообщения клиенту: {e}")
                            other_client.close()
                            clients.remove(other_client)
                            addresses.remove(other_address)
        except Exception as e:
            print(f"Ошибка: {e}")
            break

    # Закрытие соединения и удаление клиента из списка
    client_socket.close()
    index = clients.index(client_socket)
    username = addresses[index]
    clients.remove(client_socket)
    addresses.pop(index)
    print(f"{Fore.RED}Пользователь {username} отключился.")

def send_server_messages(clients):
    while True:
        message = input(" ")
        for client in clients:
            try:
                client.send(f"Сервер: {message}".encode('utf-8'))
            except Exception as e:
                print(f"Ошибка отправки сообщения клиенту: {e}")
                client.close()

def main():
    host, port = input("Введите хост и порт для сервера (host:port): ").split(':')
    port = int(port)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Сервер запущен на {host}:{port}")

    clients = []
    addresses = []

    # Запуск потока для обработки входящих сообщений с сервера
    server_message_thread = threading.Thread(target=send_server_messages, args=(clients,))
    server_message_thread.start()

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"{Fore.GREEN}{client_address} присоединился.")

        # Добавление клиента в список
        clients.append(client_socket)
        addresses.append(client_address)

        # Запуск потока для обработки клиента
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, addresses))
        client_thread.start()

if __name__ == "__main__":
    main()
