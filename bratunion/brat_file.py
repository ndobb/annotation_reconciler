import os
import sys
from copy import copy
from bratunion.brat_row import BratRow

class BratFile:

    def __init__(self, filepath: str = None):
        
        self.path = ''
        self.rows = []

        if filepath is not None:
            self.path = os.path.basename(filepath)
            with open(filepath) as fp:
                for line in fp:
                    row = BratRow(filepath, line)
                    if (row.valid()):
                        self.rows.append(row)

    def union_rows(self, comparator):
        A = self
        B = comparator

        make_row_id = lambda x: f'{x.indices.index_type}|{x.indices.start}|{x.indices.end}'

        # Assign parent ids, then union
        for row in A.rows:
            row.set_annotator_id('A')
        for row in B.rows:
            row.set_annotator_id('B')
        union = A.rows + B.rows
        final = []
        done = set()

        # For rows in union
        for a in union:

            # Add to set of rows checked
            has_match = False
            a_id = make_row_id(a)

            if a_id in done:
                continue

            # For rows in union
            for b in union:

                # If [a] and [b] are different
                b_id = make_row_id(b)
                if (a != b and a.annotator_id != b.annotator_id and b_id not in done):

                    # Check if they match (returns list)
                    matched = a.check_row_match(b, a_id, b_id)

                    if len(matched) > 0:
                        has_match = True

                        for match in matched:
                            if match not in done:
                                if match == a_id:
                                    final += [ a ]
                                else:
                                    final += [ b ]
                                done.add(match)
                        continue

            if has_match == False:
                self.log_event(a, "Row only found with one annotator")
                final.append(a)
                done.add(a_id)
        
        return final

    def log_event(self, row, text):
        row_text = row.text.replace('"', '\"')
        row_info = f'start: {row.indices.start}, end: {row.indices.end}, label: "{row.indices.index_type}", span: "{row_text}"'
        sys.stdout.write(f'{{ File: "{os.path.basename(row.file_name)}", Event: "{text}...", RowA: {{ {row_info} }} }}')
        sys.stdout.write('\n')

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
        gold.rows = self.union_rows(comparator)
        
        rows_sorted = sorted(gold.rows, key=lambda x: x.indices.start)
        for r in rows_sorted:
            r.id = f'T{row_cnt}'
            row_cnt += 1
        gold.rows = rows_sorted

        return gold