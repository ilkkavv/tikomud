# Initialize places/rooms as placeholders

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

places = {
    'place1': {
        'name': 'place1',
        'description': read_file('place1.txt'),
        'items': [],
        'exits': {
            'north': None,
            'east': None,
            'south': None,
            'west': None
        }
    },
        'place2': {
        'name': 'place2',
        'description': read_file('place2.txt'),
        'items': [],
        'exits': {
            'north': None,
            'east': None,
            'south': None,
            'west': None
        }
    },
}