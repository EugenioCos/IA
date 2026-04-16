import socket, json
import time

from connection.http import Http

class Server:

    HOST = "0.0.0.0"
    PORT = 5433

    def __init__(self):
        self.http = Http()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(1)
        self.conn = None
        self.reader = None
        self.waiting = False

    def close(self):
        self.socket.close()
        self.conn.close()

    def send_function(self, message: dict) -> any:
        while self.waiting: time.sleep(1/1000)
        self.waiting = True
        print(f"Sending {str(message["command"])}")
        to_send = self.http.compose_response(json.dumps(message))
        self.conn.sendall(bytearray(to_send))
        self.http.read_headers(self.reader)
        response = self.http.read_body(self.reader)
        data_json = json.loads(response)
        print(f"Message received")
        self.waiting = False
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
            agents_dict = data_json["agents"]
            job_dict = data_json["job"]
            orchestrator_agent_model = data_json["multi_agent_model"]
            model = data_json["model"]
        except:
            to_send = self.http.compose_response("Denied")
            self.conn.sendall(bytearray(to_send))
            return [None, None, None]
        return [orchestrator_agent_model, model, agents_dict, job_dict]

