import os
import shutil
from src.brat_file import BratFile

def get_annotator_files(path):
    files = []
    for file in os.listdir(path):
        if file.endswith(".ann"):
            files.append(file)
    return files

def get_brat_objects(path):
    files = get_annotator_files(path)
    brats = []
    for file in files:
        filepath = os.path.join(path, file)
        brat = BratFile(filepath)
        brats.append(brat)
    return brats

def make_clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def save_gold_file(out_dir: str, file: BratFile):
    f = open(os.path.join(out_dir, file.path), "w+")
    separator = '\t'

    for row in file.rows:
        f.write(f'{row.to_string()}\r\n')
    
    f.close()
            

def intersect():
    currDir = os.getcwd()

    # Get annotations
    anno1 = get_brat_objects(os.path.join(currDir, "input", "annotator1"))
    anno2 = get_brat_objects(os.path.join(currDir, "input", "annotator2"))

    # Prep output directory
    out_dir = os.path.join(currDir, "output", "intersection")
    make_clean_dir(out_dir)

    for anno in anno1:

        # Find matching Brat file
        matches = [brat for brat in anno2 if brat.path == anno.path]
        cnt = len(matches)

        if cnt == 0:
            print(f'No matches found for "{anno.path}""')
            continue

        if cnt > 1:
            print(f'{cnt} matches were unexpectedly found for "{anno.path}". Taking only the first...')

        file_match = matches[0]
        gold = anno.intersect(file_match)
        save_gold_file(out_dir, gold)

intersect()