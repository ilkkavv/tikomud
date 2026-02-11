import socket

class ClientConnection:

    def __init__(self, host, port, incoming_queue, stop_event, buff_size=1024):
        self.host = host
        self.port = port
        self.incoming_queue = incoming_queue
        self.stop_event = stop_event
        self.socket = None
        self.buff_size = buff_size

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def close(self):
        self.stop_event.set()
        try:
            if self.socket:
                self.socket.close()
        except OSError:
            pass
