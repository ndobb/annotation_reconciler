import os
import sys

class Indices:
    def __init__(self, type, start, end):

        # print(f'Start Index: {start}')
        self.index_type = type
        self.start = self.stringToIndexInt(start)
        self.end = self.stringToIndexInt(end)

    def stringToIndexInt(self, idx):

        splt = idx.split(';')
        if len(splt) > 1:
            return -1

        val = splt[0]
        if val.isnumeric():
            return int(val)
            
        return -1

class BratRow:
    def __init__(self, file_name: str, row: str):

        self.id = None
        self.indices = None
        self.text = None
        self.annotator_id = None
        self.file_name = file_name

        entity = row.split()
        if len(entity) >= 4:
            self.id = entity[0]
            self.indices = Indices(entity[1], entity[2], entity[3])
            self.text = ' '.join(entity[4:])

    def set_annotator_id(self, annotator_id):
        self.annotator_id = annotator_id

    def valid(self):
        return self.id is not None and self.indices.start > -1 and self.indices.end > -1

    def to_string(self):
        separator = '\t'
        return f'{self.id}{separator}{self.indices.index_type} {self.indices.start} {self.indices.end}{separator}{self.text}'

    def log_event(self, text, comparator):
        a_text = self.text.replace('"', '\"')
        b_text = comparator.text.replace('"', '\"')
        row_a_info = f'start: {self.indices.start}, end: {self.indices.end}, label: "{self.indices.index_type}", span: "{a_text}"'
        row_b_info = f'start: {comparator.indices.start}, end: {comparator.indices.end}, label: "{comparator.indices.index_type}", span: "{b_text}"'

        sys.stdout.write(f'{{ File: "{os.path.basename(self.file_name)}", Event: "{text}...", RowA: {{ {row_a_info} }}, RowB: {{ {row_b_info} }} }}')
        sys.stdout.write('\n')

    def check_row_match(self, comparator, a_id, b_id):
        A = self
        B = comparator

        ''' 
            1. If there are two overlapping spans with the same label - 
            include in the gold standard the span with the longest span 
            (delete the shorter one) - create a log of it. 
        '''
        # Same label
        if \
            A.indices.index_type == B.indices.index_type and \
            (
                (
                    # A begins inside B
                    A.indices.start > B.indices.start and
                    A.indices.start < B.indices.end
                ) or \
                (
                    # B begins inside A
                    B.indices.start > A.indices.start and
                    B.indices.start < A.indices.end
                )
            ):
            lenA = A.indices.end - A.indices.start
            lenB = B.indices.end - B.indices.start

            if (lenA > lenB):
                self.log_event("Rows A and B overlap and match labels but A's span is longer. Taking A and deleting B", B)
                return [ a_id ]
            else:
                self.log_event("Rows A and B overlap and match labels but B's span is longer. Taking B and deleting A", B)
                return [ b_id ]

        # Same span
        elif A.indices.start == B.indices.start and \
            A.indices.end == B.indices.end:

            ''' 
                2. if the same span has two different labels — 
                include both labels and create a log of it.
            '''

            # Different label
            if A.indices.index_type != B.indices.index_type:
                self.log_event("Rows A and B match start and end indexes but have different labels. Including both", B)
                return [ a_id, b_id ]

            # Same label
            self.log_event("Rows A and B match start and end indexes and labels. Taking only one (A)", B)
            return [ a_id ]
        
        return []