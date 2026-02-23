import queue
import threading

from tikomud.client.networking.connection import ClientConnection
from tikomud.client.ui.curses_ui import run
from tikomud.client.networking.command import send_validated

def main() -> None:
    host = "127.0.0.1"
    port = 7537

    incoming_queue: "queue.Queue" = queue.Queue()
    stop_event = threading.Event()

    conn = ClientConnection(host, port, incoming_queue, stop_event)

    def send_fn(user_input: str):
        return send_validated(conn, user_input)

    try:
        conn.connect()
        conn.start_receiver()

        run(send_fn=send_fn, incoming_queue=incoming_queue, stop_event=stop_event)

    finally:
        conn.close()

if __name__ == "__main__":
    main()