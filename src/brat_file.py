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

    def get_match(self, comparator):

        # Look for a match by exact indices
        matches = [row for row in self.rows if 
            comparator.indices.start == row.indices.start and 
            comparator.indices.end == row.indices.end and 
            comparator.indices.index_type == row.indices.index_type
        ]
    
        if len(matches) > 0:
            return matches[0]
    
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
            existing = gold.get_match(row)
            if existing is None:
                new_row = copy(row)
                gold.rows.append(new_row)
        
        rows_sorted = sorted(gold.rows, key=lambda x: x.indices.start)
        for r in rows_sorted:
            r.id = f'T{row_cnt}'
            row_cnt += 1
        gold.rows = rows_sorted

        return gold