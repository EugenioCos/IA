import socket, json

from connection.http import Http

class Server:

    HOST = "0.0.0.0"
    PORT = 5433

    def __init__(self):
        self.agents_dict = None
        self.job_dict = None
        self.model = None
        self.http = Http()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(1)
        self.conn = None
        self.reader = None

    def close(self):
        self.socket.close()
        self.conn.close()

    def send_function(self, message: dict) -> any:
        print(f"Sending {str(message["command"])}")
        to_send = self.http.compose_response(json.dumps(message))
        self.conn.sendall(bytearray(to_send))
        self.http.read_headers(self.reader)
        response = self.http.read_body(self.reader)
        data_json = json.loads(response)
        print(f"Message received")
        return data_json["response"]

    def accept_work(self) -> list:
        print(f"[CONNECTION] Waiting...")
        self.conn, addr = self.socket.accept()
        print(f"[CONNECTION] Connected")
        self.reader = self.conn.makefile('r', encoding='utf-8')
        print(f"[CONNECTION] Reading header...")
        header = self.http.read_headers(self.reader)
        print(f"[CONNECTION] Header: {header}")
        print(f"[CONNECTION] Reading body...")
        body = self.http.read_body(self.reader)
        print(f"[CONNECTION] Parsing body...")
        try:
            data_json = json.loads(body)
            self.agents_dict = data_json["agents"]
            self.job_dict = data_json["job"]
            self.model = data_json["model"]
        except:
            to_send = self.http.compose_response("Denied")
            self.conn.sendall(bytearray(to_send))
            return [None, None, None]
        return [self.model, self.agents_dict, self.job_dict]

