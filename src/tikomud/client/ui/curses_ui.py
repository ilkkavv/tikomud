import curses
import queue
import textwrap

from typing import Any

def render_incoming(msg: Any) -> str:
    if isinstance(msg, str):
        return msg

    if isinstance(msg, dict):
        mtype = msg.get("type")

        if mtype == "chat":
            t = msg.get("time", "")
            sender = msg.get("sender", "Unknown")
            text = msg.get("message", "")
            if t:
                return f"{t} [{sender}]: {text}"
            return f"[{sender}]: {text}"

        if mtype == "system":
            return msg.get("message", "")

        if mtype == "error":
            code = msg.get("code", "ERROR")
            text = msg.get("message", "")
            return f"{code}: {text}" if text else str(code)

        if mtype == "text":
            return msg.get("message", "")

        return str(msg)

    return str(msg)

def print_msg(messages, msg) -> None:
    if not isinstance(msg, str):
        msg = str(msg)

    for raw_line in msg.splitlines() or [""]:
        wrapped = textwrap.wrap(raw_line, width=120)  # tai anna width draw()sta
        if not wrapped:
            messages.append("")
        else:
            messages.extend(wrapped)

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
                incoming = incoming_queue.get_nowait()
                line = render_incoming(incoming)
                if line:
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

        # Backspace support
        if key in (curses.KEY_BACKSPACE, 127, 8):
            current_input = current_input[:-1]
            continue

        if key in (10, 13):  # Enter
            msg = current_input.strip()
            current_input = ""

            if not msg:
                continue

            local_msg = send_fn(msg)
            if local_msg:
                print_msg(messages, str(local_msg))
            continue

        if 32 <= key <= 126:
            current_input += chr(key)

def run(send_fn, incoming_queue, stop_event) -> None:
    curses.wrapper(lambda stdscr: _main(stdscr, send_fn, incoming_queue, stop_event))