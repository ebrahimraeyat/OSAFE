import find_etabs

def open(filename):
    insert(filename)

def insert(filename):
    find_etabs.find_etabs(
        run=False,
        backup=False,
        software='OSAFE',
        filename=filename,
        )
