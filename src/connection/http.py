
class Http:
    
    def create_header(self, body_size) -> bytes:
        header = [
            f"HTTP/1.1 200 OK",
            "Content-Type: application/json; charset=utf-8",
            f"Content-Length: {body_size}"
        ]
        joined_header = "\r\n".join(header) + "\r\n\r\n"
        return joined_header.encode(encoding="utf-8")

    def create_body(self, data: str) -> bytes:
        body = f"{data}\r\n"
        return body.encode(encoding="utf-8")
    
    def compose_response(self, text: str):
        body = self.create_body(text)
        header = self.create_header(len(body))
        return header + body

    def read_body(self, reader):
        return reader.readline()
    
    def read_headers(self, reader):
        data = ""
        while True:
            line = reader.readline()
            if line is None or line in ("\r\n", "\n", ""):
                break
            data += line
        return data
