import os
import sys
from copy import copy
from bratmerge.brat_row import BratRow

STUDENT = 'STUDENT'
I2B2 = 'I2B2'

# Student labels
ADDRESS = 'ADDRESS'
AGE = 'AGE'
DATE = 'DATE'
EMAIL = 'EMAIL'
ID = 'ID'
NAME = 'NAME'
PHONE_OR_FAX = 'PHONE_OR_FAX'
PROFESSION = 'PROFESSION'
URL = 'URL'

# i2b2 labels
NAME_SUBCATS = set([ 'PATIENT', 'DOCTOR', 'USERNAME', NAME ])
LOC_SUBCATS = set([ 'HOSPITAL', 'COUNTRY', 'ORGANIZATION', 'ZIP', 'STREET', 'CITY', 'STATE', 'LOCATION-OTHER', ADDRESS ])
CONTACT_SUBCATS = set([ 'PHONE', 'FAX', 'EMAIL', 'URL', 'IPADDR', PHONE_OR_FAX ])
ID_SUBCATS = set([ 'MEDICALRECORD', 'SSN', 'ACCOUNT', 'LICENSE', 'DEVICE', 'IDNUM', 'BIOID', 'HEALTHPLAN', 'VEHICLE', ID ])

UNKNOWN = 'UNKNOWN'

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

    def merge_rows(self, comparator):

        ''' 
            - Name: take i2b2 label when there is an overlap 
            - Profession: take student label
            - Location: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
            - Age: take student label 
            - Date: take student label 
            - Contact: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
            - ID: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
        '''

        student = self
        i2b2 = comparator

        make_row_id = lambda x: f'{x.indices.index_type}|{x.indices.start}|{x.indices.end}'
        i2b2.rows = [ row for row in i2b2.rows if row.indices.index_type not in [ AGE, DATE, PROFESSION ]]

        # Assign parent ids, then union
        for row in student.rows:
            row.set_annotator_id(STUDENT)
        for row in i2b2.rows:
            row.set_annotator_id(I2B2)
        union = student.rows + i2b2.rows
        final = []
        done = set()

        # For student rows in union
        for std in union:

            # Add to set of rows checked
            has_match = False
            std_id = make_row_id(std)

            if std_id in done:
                continue

            # For i2b2 rows in union
            for i2 in union:
                
                # Check overlap
                student_inside_i2b2 = std.indices.start >= i2.indices.start and std.indices.start <= i2.indices.end
                i2b2_inside_student = i2.indices.start >= std.indices.start and i2.indices.start <= std.indices.end

                if not student_inside_i2b2 and not i2b2_inside_student:
                    continue

                # If [std] and [i2b2] are different
                i2b2_id = make_row_id(i2)
                if (std != i2 and std.annotator_id != i2.annotator_id and i2b2_id not in done):

                    # Check if they match (returns list)
                    matched = std.check_row_match(i2, std_id, i2b2_id)

                    if len(matched) > 0:
                        has_match = True

                        for match in matched:
                            if match not in done:
                                if match == std_id:
                                    final += [ std ]
                                else:
                                    final += [ i2 ]
                                done.add(match)
                        continue

            if has_match == False:

                # Only keep unmatched student row if an age, date, or profession
                if std.indices.index_type in [ AGE, DATE, PROFESSION ]:
                    self.log_event(std, "Student row was not matched with i2b2 annotations but will be allowed.")
                    final.append(std)
                    done.add(std_id)
                elif std.indices.index_type in LOC_SUBCATS or \
                     std.indices.index_type in CONTACT_SUBCATS or \
                     std.indices.index_type in ID_SUBCATS:
                    self.log_event(std, "Student row was not matched with i2b2 annotations. Setting to 'UNKNOWN'.")
                    std.indices.index_type = UNKNOWN
                    final.append(std)
                    done.add(std_id)

        # Get unmatched i2b2 records
        i2b2_unmatched = [ i2 for i2 in i2b2.rows if make_row_id(i2) not in done ]
        for unmatched in i2b2_unmatched:
            if unmatched.indices.index_type in LOC_SUBCATS or \
               unmatched.indices.index_type in CONTACT_SUBCATS or \
               unmatched.indices.index_type in ID_SUBCATS:
               self.log_event(unmatched, "i2b2 row was not matched in student annotations. Setting to 'UNKNOWN'")
               unmatched.indices.index_type = UNKNOWN
               final.append(unmatched)
        
        return final

    def log_event(self, row, text):
        row_text = row.text.replace('"', '\"')
        row_info = f'start: {row.indices.start}, end: {row.indices.end}, label: "{row.indices.index_type}", span: "{row_text}"'
        sys.stdout.write(f'{{ File: "{os.path.basename(row.file_name)}", Event: "{text}...", RowA: {{ {row_info} }} }}')
        sys.stdout.write('\n')

    def merge(self, comparator):
        gold = BratFile()
        gold.path = self.path
        row_cnt = 1
        gold.rows = self.merge_rows(comparator)
        rows_sorted = sorted(gold.rows, key=lambda x: x.indices.start)
        for r in rows_sorted:
            r.id = f'T{row_cnt}'
            row_cnt += 1
        gold.rows = rows_sorted

        return gold