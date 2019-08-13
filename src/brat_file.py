import os
import copy
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

        for row in comparator.rows:
            match: BratRow = comparator.get_match(row)
            if match is not None:
                match.id = f'T{row_cnt}'
                gold.rows.append(match)
                row_cnt += 1

        return gold
        
    def union(self, comparator):
        gold = BratFile()
        gold.path = self.path
        row_cnt = 1

        for row in self.rows:
            new_row = copy.copy(row)
            new_row.id = f'T{row_cnt}'
            gold.rows.append(new_row)

        return gold