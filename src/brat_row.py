
class Indices:
    def __init__(self, type, start, end):

        # print(f'Start Index: {start}')
        self.index_type = type
        self.start = self.stringToIndexInt(start)
        self.end = self.stringToIndexInt(end)

    def stringToIndexInt(self, idx):

        splt = idx.split(';')
        val = splt[0]
        if val.isnumeric():
            return int(val)
        return -1

class BratRow:
    def __init__(self, row: str):

        self.id = None
        self.indices = None
        self.text = None

        entity = row.split()
        if len(entity) >= 4:
            self.id = entity[0]
            self.indices = Indices(entity[1], entity[2], entity[3])
            self.text = ' '.join(entity[4:])

    def valid(self):
        return self.id is not None and self.indices.start > -1 and self.indices.end > -1

    def to_string(self):
        separator = '\t'
        return f'{self.id}{separator}{self.indices.index_type} {self.indices.start} {self.indices.end}{separator}{self.text}'