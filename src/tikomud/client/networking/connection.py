class ClientConnection:

    def __init__(self, host, port, incoming_queue, stop_event, buff_size=1024):
        self.host = host
        self.port = port
        self.incoming_queue = incoming_queue
        self.stop_event = stop_event
        self.socket = None
        self.buff_size = buff_size
