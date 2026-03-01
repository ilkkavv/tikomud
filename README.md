# TIKOMUD

TIKOMUD is a MUD-style multiplayer text adventure and role-playing game developed as a team project.

The project focuses on collaborative Git workflows, branch-based development, and structured releases while building a shared text-based game world.

⚠️ **Work in Progress**

This project is currently under active development. The game is not feature-complete and core systems are still being implemented.

---

## Current Features (Release 0.2.0)

- Basic client-server architecture
- Player name input on launch
- Send messages to other players
- Move between different rooms
- Interactive NPC system

---

## Planned Core Features (Not Yet Implemented)

The following major systems are still missing:

- Authentication / proper login system
- Persistent world (data saving)
- Character stats and progression
- Items and equipment system
- Monsters and combat system
- Dialogue system

---

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

### How to Play

- Start the server.
- Launch the client.
- Enter your player name when prompted.
- Available commands:
  - `yell` – broadcast message to all connected players
  - `say` – broadcast message to players in the same room
  - `inv` – display player inventory (currently empty)
  - `move | m | go <direction>` – move to the given direction
  - `talk <npc>` – talk to an NPC

More gameplay systems will be introduced in future releases.
