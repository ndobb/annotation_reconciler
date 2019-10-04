import os
from copy import copy
from src.brat_row import BratRow

class BratFile:

    def __init__(self, filepath: str = None):
        
        self.path = ''
        self.rows = []

        if filepath is not None:
            self.path = os.path.basename(filepath)
            with open(filepath) as fp:
                for line in fp:
                    row = BratRow(line)
                    if (row.valid()):
                        self.rows.append(BratRow(line))

    def get_row_match(self, comparator, strict):
        if strict == True:
            return get_strict_match(self, comparator)
        return get_overlap_label_match(self, comparator)

    def get_strict_match(self, comparator):

        # Look for a match by exact indices
        matches = [row for row in self.rows if 
            comparator.indices.start == row.indices.start and 
            comparator.indices.end == row.indices.end and 
            comparator.indices.index_type == row.indices.index_type
        ]
    
        if len(matches) > 0:
            return matches[0]
    
        return None

    def get_overlap_label_match(self, comparator):

        for row in self.rows:

            A = self
            B = comparator

            ''' 1. If there are two overlapping spans with the same label - 
                include in the gold standard the span with the longest span 
                (delete the shorter one) - create a log of it. 
            '''
            # Same label
            if \
                A.indices.index_type == B.indices.index_type and \
                (
                    # A begins inside B
                    A.indices.start > B.indices.start and
                    A.indices.start < B.indices.end
                ) or \
                (
                    # B begins inside A
                    B.indices.start > A.indices.start and
                    B.indices.start < A.indices.end
                ):
                lenA = len(A.indices.end - A.indices.start) 
                lenB = len(B.indices.end - B.indices.start)

                if (lenA > lenB):
                    return [ A ]
                else:
                    return [ B ]

            # Same span
            elif A.indices.start == B.indices.start and \
                A.indices.end == B.indices.end:

                ''' 2. if the same span has two different labels — 
                    include both labels and create a log of it.
                '''

                # Different label
                if A.indices.index_type != B.indices.index_type:
                    return [ A, B ]

                # Same label
                return [ A ]

        return None

    def intersect(self, comparator):
        gold = BratFile()
        gold.path = self.path
        row_cnt = 1

        for row in self.rows:
            match: BratRow = comparator.get_match(row)
            if match is not None:
                new_row = copy(match)
                new_row.id = f'T{row_cnt}'
                gold.rows.append(new_row)
                row_cnt += 1

        return gold
        
    def union(self, comparator):
        gold = BratFile()
        gold.path = self.path
        row_cnt = 1

        for row in self.rows:
            new_row = copy(row)
            gold.rows.append(new_row)

        for row in comparator.rows:
            existing = gold.get_row_match(row, False)
            if existing is None:
                new_row = copy(row)
                gold.rows.append(new_row)
        
        rows_sorted = sorted(gold.rows, key=lambda x: x.indices.start)
        for r in rows_sorted:
            r.id = f'T{row_cnt}'
            row_cnt += 1
        gold.rows = rows_sorted

        return gold