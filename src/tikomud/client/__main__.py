import queue
import threading

from tikomud.client.networking.connection import ClientConnection
from tikomud.client.ui.curses_ui import run
from tikomud.client.networking.command import send_validated  # validate + JSON send wrapper

# main.py
def main() -> None:
    host = "127.0.0.1"
    port = 7537

    incoming_queue: "queue.Queue" = queue.Queue()
    stop_event = threading.Event()

    conn = ClientConnection(host, port, incoming_queue, stop_event)

    name_sent = False
    in_dialogue = False  # <--- add this

    def send_fn(user_input: str):
        nonlocal name_sent, in_dialogue

        # First input = player name -> send as plain string
        if not name_sent:
            conn.send_line(user_input)
            name_sent = True
            return None

        # Send validated command, passing in_dialogue
        local_msg = send_validated(conn, user_input, in_dialogue=in_dialogue)

        # Check if this is starting a conversation
        if user_input.lower().startswith("talk "):
            in_dialogue = True

        return local_msg

    try:
        conn.connect()
        conn.start_receiver()
        run(send_fn=send_fn, incoming_queue=incoming_queue, stop_event=stop_event, in_dialogue_flag=lambda: in_dialogue)
    finally:
        conn.close()

if __name__ == "__main__":
    main()