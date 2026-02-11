import socket
import threading

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

    def start_receiver(self):
        thread = threading.Thread(target=self._receiver_loop, daemon=True)
        thread.start()

    def _receiver_loop(self):
        buffer = ""

        while not self.stop_event.is_set():
            try:
                data = self.socket.recv(self.buff_size)
                if not data:
                    self.incoming_queue.put("Server closed the connection.")
                    self.stop_event.set()
                    break

                buffer += data.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.rstrip("\r")
                    if line:
                        self.incoming_queue.put(line)

            except OSError:
                self.incoming_queue.put("Connection lost.")
                self.stop_event.set()
                break

    def send(self, text):
        if not self.socket:
            return
        self.socket.sendall((text + "\n").encode("utf-8"))
