import curses
import queue

def print_msg(messages, msg: str) -> None:
    messages.append(msg)

def draw(stdscr, messages, current_input: str) -> None:
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    max_lines = height - 2
    visible = messages[-max_lines:]

    for i, line in enumerate(visible):
        stdscr.addnstr(i, 0, line, width - 1)

    stdscr.hline(height - 2, 0, curses.ACS_HLINE, width)

    prompt = "> "
    stdscr.addnstr(height - 1, 0, prompt + current_input, width - 1)

    stdscr.refresh()

def _main(stdscr, send_fn, incoming_queue, stop_event) -> None:
    curses.curs_set(1)
    stdscr.keypad(True)
    stdscr.timeout(50)

    messages = ["Welcome to TIKOMUD!", "What shall you be known as?"]
    current_input = ""

    while True:
        try:
            while True:
                line = incoming_queue.get_nowait()
                print_msg(messages, line)
        except queue.Empty:
            pass

        if stop_event.is_set():
            print_msg(messages, "Disconnected.")
            draw(stdscr, messages, "")
            break

        draw(stdscr, messages, current_input)

        key = stdscr.getch()

        if key == -1:
            continue

        # Implemented backspace support.
        if key in (curses.KEY_BACKSPACE, 127, 8):
            current_input = current_input[:-1]

        if key in (10, 13): # Enter
            msg = current_input.strip()
            current_input = ""

            if not msg:
                continue

            send_fn(msg)
            continue

        if 32 <= key <= 126:
            current_input += chr(key)


def run(send_fn, incoming_queue, stop_event) -> None:
    curses.wrapper(lambda stdscr: _main(stdscr, send_fn, incoming_queue, stop_event))
