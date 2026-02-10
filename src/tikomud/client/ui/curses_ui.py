import curses

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

def _main(stdscr) -> None:
    curses.curs_set(1)
    stdscr.keypad(True)

    messages = ["Welcome to TIKOMUD!"]
    current_input = ""

    while True:
        draw(stdscr, messages, current_input)

        key = stdscr.getch()

        if key in (10, 13): # Enter
            msg = current_input.strip()
            if msg:
                print_msg(messages, msg)
            current_input = ""
            continue

        if 32 <= key <= 126:
            current_input += chr(key)

def run() -> None:
    curses.wrapper(_main)
