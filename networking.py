import socket
import threading
import json

NYZON_PORT = 51250
NETWORKPY_PORT = 51251

server_globalsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
publicsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

main_list = []

def newsocket():
    publicsock.bind(('localhost', 0))
    return publicsock.getsockname()[1]

bogus_item = {
    "name": "None",
    "description": "None",
    "instock": False,
    "howmanyinstock": 0,
    "price": 0.0
}

def find_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))  # Bind to a random available port on localhost
    port = sock.getsockname()[1]  # Get the port number
    sock.close()
    return port

class Server:
    def __init__(self, host='localhost', port=None):
        self.host = host
        if port is None:
            port = find_free_port()  # Use a random free port if not specified
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        self.clients = {}
        
    def start(self):
        while True:
            client, address = self.sock.accept()
            print(f"Connection from {address}")
            threading.Thread(target=self.handle_client, args=(client,)).start()
            
    def handle_client(self, client):
        try:
            data = client.recv(1024).decode()
            if data.startswith("HELLO"):
                username = data.split()[1]
                self.clients[client] = username
                client.sendall("WELCOME".encode())
            else:
                client.sendall("ERROR".encode())

            while True:
                data = client.recv(1024).decode()
                if not data:
                    break
                print(f"Received from {self.clients[client]}: {data}")
                response = self.process_request(data)
                client.sendall(response.encode())
        except Exception as e:
            print(f"Error: {e}")
            client.sendall(json.dumps([bogus_item]).encode())
        finally:
            client.close()
            if client in self.clients:
                del self.clients[client]
            
    def process_request(self, request):
        parts = request.split()
        if len(parts) == 0:
            return json.dumps([bogus_item])
        
        command = parts[0]

        if command == "APPENDGROUP":
            if len(main_list) < 5:
                main_list.append([])
                return json.dumps({"status": "success", "message": "Appended new item group"})
            else:
                return json.dumps({"status": "error", "message": "Main list is full"})
        
        elif command == "APPENDITEM":
            try:
                group_index = int(parts[1])
                item_data = json.loads(' '.join(parts[2:]))
                if len(main_list[group_index]) < 5:
                    main_list[group_index].append(item_data)
                    publicsock.sendall(json.dumps)|
({"status": "success", "message": f"Appended item to group {group_index}"}).encode())
                    return json.dumps({"status": "success", "message": f"Appended item to group {group_index}"})
                else:
                    return json.dumps({"status": "error", "message": "Item group is full"})
            except IndexError:
                return json.dumps({"status": "error", "message": "Group index out of range"})
            except ValueError:
                return json.dumps({"status": "error", "message": "Invalid group index or item data"})

        elif command == "GETLIST":
            return json.dumps(main_list)
        
        else:
            return json.dumps([bogus_item])

class UserNode:
    def __init__(self, username, host='localhost', port=NYZON_PORT):
        self.username = username
        self.host = host
        self.port = port
        self.connect_to_server()

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            self.sock.sendall(f"HELLO {self.username}".encode())
            response = self.sock.recv(1024).decode()
            if response != "WELCOME":
                raise Exception("Failed to connect to server")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.sock.close()
            self.sock = None

    def server_ask_append_group(self):
        if self.sock:
            try:
                self.sock.sendall("APPENDGROUP".encode())
                response = self.sock.recv(1024).decode()
                print(response)
            except Exception as e:
                print(f"Error sending request to server: {e}")
        else:
            print("Socket is not connected")

    def server_ask_append_item(self, group_index, item_data):
        if self.sock:
            try:
                request_data = f"APPENDITEM {group_index} {json.dumps(item_data)}"
                self.sock.sendall(request_data.encode())
                response = self.sock.recv(1024).decode()
                print(response)
            except Exception as e:
                print(f"Error sending request to server: {e}")
        else:
            print("Socket is not connected")

    def server_ask_getlist(self):
        if self.sock:
            try:
                self.sock.sendall("GETLIST".encode())
                response = self.sock.recv(1024).decode()
                return json.loads(response)
            except Exception as e:
                print(f"Error sending request to server: {e}")
        else:
            print("Socket is not connected")

    def close_connection(self):
        if self.sock:
            self.sock.close()
