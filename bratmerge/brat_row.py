import os
import sys

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

class Indices:
    def __init__(self, type, start, end):

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
        student = self
        i2b2 = comparator
        std_id = a_id
        i2b2_id = b_id

        ''' 
            - Name: take i2b2 label when there is an overlap 
            - Profession: take student label
            - Location: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
            - Age: take student label 
            - Date: take student label 
            - Contact: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
            - ID: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
        '''

        # Name: take i2b2 label when there is an overlap 
        if student.indices.index_type == NAME and i2b2.indices.index_type in NAME_SUBCATS:
            self.log_event("Student and i2b2 rows overlap and match category to subcategory. Keeping i2b2", i2b2)
            return [ i2b2_id ]

        # Age, Date, Profession: take student label
        if student.indices.index_type in [ AGE, DATE, PROFESSION ]:
            self.log_event("Student and i2b2 rows overlap and match category to subcategory. Keeping student", i2b2)
            return [ std_id ]

        # Location: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
        if student.indices.index_type == ADDRESS and i2b2.indices.index_type in LOC_SUBCATS:
            self.log_event("Student and i2b2 rows overlap and match category to subcategory. Keeping i2b2", i2b2)
            return [ i2b2_id ]

        # Contact: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
        if student.indices.index_type == PHONE_OR_FAX and i2b2.indices.index_type in CONTACT_SUBCATS:
            self.log_event("Student and i2b2 rows overlap and match category to subcategory. Keeping i2b2", i2b2)
            return [ i2b2_id ]

        # ID: take i2b2 label when there is an overlap - if not in i2b2 or not in student label unknown 
        if student.indices.index_type == ID and i2b2.indices.index_type in ID_SUBCATS:
            self.log_event("Student and i2b2 rows overlap and match category to subcategory. Keeping i2b2", i2b2)
            return [ i2b2_id ]

        return []