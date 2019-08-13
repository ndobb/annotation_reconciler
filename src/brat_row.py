
class Indices:

    def __init__(self, input: str):

        self.index_type = ''
        self.start = -1
        self.end = -1
        
        split = input.split(' ')

        if len(split) == 3:
            self.index_type = split[0]
            self.start = split[1]
            self.end = split[2]

class BratRow:

    id = None
    indices = None
    text = None

    def __init__(self, row: str):

        split = row.strip().split('\t')
        cnt = len(split)

        if cnt != 3:
            print(f'Error: only {cnt} items were found...')
            return

        self.id = split[0]
        self.indices = Indices(split[1])
        self.text = split[2]

    def valid(self):
        return self.id is not None

    def to_string(self):
        separator = '\t'
        return f'{self.id}{separator}{self.indices.index_type} {self.indices.start} {self.indices.end}{separator}{self.text}'