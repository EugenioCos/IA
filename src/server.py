import socket, json

class Server:
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    agents_dict = None
    job_dict = None
    model = None

    def __init__(self):
        self.agents_dict = None
        self.job_dict = None
        self.model = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(1)
        self.reader = None

    def __del__(self):
        self.socket.close()
        self.conn.close()

    def read_dict(self) -> dict:
        """Reads the stream until it hits a newline, then parses JSON."""
        line = self.reader.readline()
        while line is None:
            print(line)
            line = self.reader.readline()
        return json.loads(line)

    def send_function(self, message) -> any:
        print(f"Sending {str(message["command"])}")
        to_send = json.dumps(message).encode(encoding="utf-8")+b'\n'
        self.conn.sendall(bytearray(to_send))
        data_json = self.read_dict()
        return data_json["response"]

    def accept_work(self) -> list:
        self.conn, addr = self.socket.accept()
        print(f"[CONNECTION] Connected")
        self.reader = self.conn.makefile('r', encoding='utf-8')
        data_json = self.read_dict()
        self.conn.sendall(b'OK\n')
        print(f"[CONNECTION] Sended OK")
        self.agents_dict = data_json["agents"]
        self.job_dict = data_json["job"]
        self.model = data_json["model"]
        return [self.model, self.agents_dict, self.job_dict]

