# TIKOMUD

TIKOMUD is a MUD-style multiplayer text adventure and role-playing game developed as a team project.

The project focuses on collaborative Git workflows, branch-based development, and structured releases while building a shared text-based game world.

## Installation & Running

### Requirements
- Python 3.10+
- Linux / WSL (curses is required)

### Clone the repository
```bash
git clone https://github.com/ilkkavv/tikomud
cd tikomud
```

### Running the server
Open a terminal:
```bash
cd tikomud/src
python3 -m tikomud.server
```

### Running the client (TUI)
Open another terminal:
```bash
cd tikomud/src
python3 -m tikomud.client
```
