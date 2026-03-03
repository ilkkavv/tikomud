class Item:

    # Basic representation of an item in the game world.
    def __init__(self, key: str, name: str, qty: int = 1, desc: str = ""):
        self.key = key
        self.name = name
        self.qty = qty
        self.desc = desc
