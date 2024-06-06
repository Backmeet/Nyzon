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
                    publicsock.sendall(json.dumps
