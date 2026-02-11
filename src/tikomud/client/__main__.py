import queue
import threading

from tikomud.client.networking.connection import ClientConnection
from tikomud.client.ui.curses_ui import run

def main() -> None:
    host = "127.0.0.1"
    port = 7537

    incoming_queue: "queue.Queue[str]" = queue.Queue()
    stop_event = threading.Event()

    conn = ClientConnection(host, port, incoming_queue, stop_event)

    try:
        conn.connect()
        conn.start_receiver()

        run(send_fn=conn.send, incoming_queue=incoming_queue, stop_event=stop_event)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
