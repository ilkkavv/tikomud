def start_dialogue(player, npc):
    player.active_dialogue = npc.id
    player.dialogue_node = "start"
    return get_current_node(npc, player)

def get_current_node(npc, player):
    node_id = player.dialogue_node
    return npc.dialogue.get(node_id)
