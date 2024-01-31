import socket
import threading
from colorama import Fore, Style, init
from colorama import just_fix_windows_console
import time
import os

init()
just_fix_windows_console()

print_lock = threading.Lock()

def receive_messages(client_socket):
    while True:
        try:
            response = client_socket.recv(1024)
            if not response:
                print("")

            with print_lock:
                print("")
                print(response.decode('utf-8'))
        except Exception as e:
            print("")
            print(f"{Fore.RED}Ошибка получения сообщения: {e}{Style.RESET_ALL}")
            print(f"{Fore.RED}Соединение разорвано.{Style.RESET_ALL}")
            print("")

# ... (ваш текущий код)

def run_client():
    try:
        server_ip = input(f"{Fore.CYAN}Айпи и порт сервера (Типо localhost:5555 или нгрок): ")
        server_ip, server_port = server_ip.split(':')
        server_port = int(server_port)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))

        nickname = input(f"{Fore.CYAN}Введи ник: ")
        color_choice = input(f"{Fore.GREEN}Выберите цвет для ника {Fore.RED}red, {Fore.GREEN}green, {Fore.YELLOW}yellow, {Fore.BLUE}blue, {Fore.MAGENTA}magenta, {Fore.CYAN}cyan, {Fore.WHITE}white {Fore.GREEN}: ")
        color_code = getattr(Fore, color_choice.upper(), Fore.WHITE)
        formatted_nickname = f"{color_code}{nickname}{Style.RESET_ALL}"

        # Отправляем серверу ник и код цвета
        client.send(f"{formatted_nickname}:{color_choice}".encode('utf-8'))

        print(f"{Fore.CYAN}Ты зашел к {server_ip}:{server_port} как {formatted_nickname}{Style.RESET_ALL}")

        threading.Thread(target=receive_messages, args=(client,)).start()

        while True:
            message = input(f"{formatted_nickname}:{Fore.WHITE} ")
            # Отправляем серверу сообщение и код цвета
            client.send(f"{message}:{color_choice}".encode('utf-8'))

    except ValueError:
        print(f"{Style.BRIGHT}{Fore.RED}Ошибка ввода. Пожалуйста, введите правильный формат (например, localhost:5555){Style.RESET_ALL}")

if __name__ == "__main__":
    run_client()


