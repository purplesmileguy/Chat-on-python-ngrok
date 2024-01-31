import socket
import threading
from colorama import Fore, Style, init
from colorama import just_fix_windows_console
from queue import Queue
import tkinter as tk
from tkinter import messagebox
import os

init()
just_fix_windows_console()
print_lock = threading.Lock()

connected_clients = []

class ServerGUI:
    def __init__(self, root, message_queue):
        self.root = root
        self.root.title("Chat Server")
        self.message_queue = message_queue

        self.clients_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        self.clients_listbox.pack(pady=10)

        self.kick_button = tk.Button(root, text="Kick", command=self.kick_client)
        self.kick_button.pack()

    def kick_client(self):
        selected_index = self.clients_listbox.curselection()
        if selected_index:
            selected_client = connected_clients[selected_index[0]]
            client_socket, client_nickname, client_lock = selected_client
            try:
                client_socket.send("You have been kicked from the server.".encode('utf-8'))
                client_socket.close()
                connected_clients.remove(selected_client)
                self.update_clients_list()
            except Exception as e:
                print(f"{Fore.RED}Ошибка кика пользователя {client_nickname}: {e}{Style.RESET_ALL}")

    def update_clients_list(self):
        self.clients_listbox.delete(0, tk.END)
        for _, client_nickname, _ in connected_clients:
            self.clients_listbox.insert(tk.END, client_nickname)

def handle_client(client_socket, client_nickname, message_queue, gui):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            decoded_data = data.decode('utf-8')
            message, color_code = decoded_data.split(':')  # Разделяем сообщение и код цвета

            formatted_message = f"{getattr(Fore, color_code.upper(), Fore.WHITE)}{client_nickname}:{Style.RESET_ALL} {message}"

            message_queue.put(formatted_message)

            for other_client_socket, other_client_nickname, _ in connected_clients:
                if other_client_nickname != client_nickname:
                    try:
                        other_client_socket.send(formatted_message.encode('utf-8'))
                    except Exception as e:
                        print(f"{Fore.RED}Ошибка отправления {other_client_nickname}:{Style.RESET_ALL} {e}")
                        connected_clients.remove((other_client_socket, other_client_nickname, _))
                        
            # Сохраняем сообщение в файл
            save_message(f"{client_nickname}: {message}")
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.RED}Похоже {Style.NORMAL}{client_nickname}{Style.BRIGHT}{Fore.RED} просто ливнул{Style.RESET_ALL}")
    finally:
        client_socket.close()
        gui.update_clients_list()

def save_message(message):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_log.txt")
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(message + "\n")

def display_messages(message_queue):
    while True:
        try:
            message = message_queue.get()
            with print_lock:
                print(message)
        except Exception as e:
            print(f"{Fore.RED}Ошибка вывода сообщения: {e}{Style.RESET_ALL}")

def run_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"{Style.BRIGHT}{Fore.BLUE}Сервер запущен на {port}.{Style.RESET_ALL}")

    message_queue = Queue()
    display_thread = threading.Thread(target=display_messages, args=(message_queue,))
    display_thread.start()

    root = tk.Tk()
    gui = ServerGUI(root, message_queue)
    gui.root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())  # Handle closing the GUI window

    server_thread = threading.Thread(target=server_thread_worker, args=(server, message_queue, gui))
    server_thread.start()

    root.mainloop()

def server_thread_worker(server, message_queue, gui):
    while True:
        client_socket, addr = server.accept()
        client_nickname, color_choice = client_socket.recv(1024).decode('utf-8').split(':')
        print(f"{Style.BRIGHT}{Fore.CYAN}{addr[0]}:{addr[1]} подключился как {client_nickname}{Style.RESET_ALL}")

        client_lock = threading.Lock()
        connected_clients.append((client_socket, client_nickname, client_lock))
        gui.update_clients_list()

        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_nickname, message_queue, gui))
        client_handler.start()

if __name__ == "__main__":
    port = int(input(f"{Fore.CYAN}Введите порт сервера:{Style.RESET_ALL} "))
    run_server(port)
