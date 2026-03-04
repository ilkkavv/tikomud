def start_dialogue(player, npc):
    player.active_dialogue = npc.id
    player.dialogue_node = "start"
    return get_current_node(npc, player)

def get_current_node(npc, player):
    node_id = player.dialogue_node
    return npc.dialogue.get(node_id)

def choose_option(player, npc, index: int):
    node = get_current_node(npc, player)
    options = node.get("options", [])

    if index < 0 or index >= len(options):
        return {"type": "error", "message": "Invalid choice."}

    next_id = options[index]["next"]

    if next_id is None:
        player.active_dialogue = None
        player.dialogue_node = None
        return {"type": "system", "message": "Conversation ended."}

    player.dialogue_node = next_id
    return get_current_node(npc, player)
