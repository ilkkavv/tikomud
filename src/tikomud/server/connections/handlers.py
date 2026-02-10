from tikomud.server.connections.clients import add_client, remove_client, broadcast

def handle_client(conn, buff_size: int) -> None:
    username = ""

    try:
        data = conn.recv(buff_size)
        if not data:
            return

        username = data.decode("utf-8", errors="replace").strip()

        if not username:
            return

        add_client(conn, username)
        print(f"{username} joined.")

        broadcast(f"{username} joined!")

        while True:
            data = conn.recv(buff_size)
            if not data:
                print(f"{username} disconnected.")
                break

            raw = data.decode("utf-8", errors="replace").strip()
            if not raw:
                continue

            broadcast(raw, conn)
    except ConnectionResetError:
        print(f"Connection reset by {username or 'unknown'}.")
    finally:
        leaving = remove_client(conn)

        if leaving:
            print(f"{leaving} left.")
            broadcast(f"{leaving} has left!")

        try:
            conn.close()
        except OSError:
            pass
