class Item:

    # Basic representation of an item in the game world.
    def __init__(self, key: str, name: str, qty: int = 1, desc: str = ""):
        self.key = (key or "").strip().lower()
        self.name = name
        self.qty = max(1, int(qty))
        self.desc = desc

    # Methods to Item class
    def add(self, amount: int = 1):
        self.qty += max(1, amount)

    def remove(self, amount: int = 1) -> bool:
        if amount > self.qty:
            return False
        self.qty -= amount
        return True

    def is_empty(self) -> bool:
        return self.qty <= 0

    # Compatibility helpers
    def to_tuple(self):
        return (self.name, self.qty, self.desc)

    def to_dict(self):
        return {
            "key": self.key,
            "name": self.name,
            "quantity": self.qty,
            "description": self.desc,
        }