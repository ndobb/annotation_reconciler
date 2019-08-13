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

def prep(dir_name: str):
    currDir = os.getcwd()

    # Get annotations
    anno1 = get_brat_objects(os.path.join(currDir, "input", "annotator1"))
    anno2 = get_brat_objects(os.path.join(currDir, "input", "annotator2"))

    # Prep output directory
    out_dir = os.path.join(currDir, "output", dir_name)
    make_clean_dir(out_dir)

    return out_dir, anno1, anno2


def intersect():
    out_dir, anno1, anno2 = prep("intersect")

    for anno in anno1:

        # Find matching Brat file
        matches = [brat for brat in anno2 if brat.path == anno.path]
        cnt = len(matches)

        if cnt == 0:
            print(f'No matches found for file "{anno.path}". Skipping file...')
            continue

        if cnt > 1:
            print(f'{cnt} matches were unexpectedly found for "{anno.path}". Taking only the first...')

        match = matches[0]
        gold = anno.intersect(match)
        save_gold_file(out_dir, gold)

def union():
    out_dir, anno1, anno2 = prep("union")

    # Check first annotator
    for anno in anno1:

        # Find matching Brat file in annotator2
        matches = [brat for brat in anno2 if brat.path == anno.path]
        cnt = len(matches)

        if cnt == 0:
            print(f'No matches found for file "{anno.path}". Saving single annotation file without union...')
            save_gold_file(out_dir, anno)
            continue

        if cnt > 1:
            print(f'{cnt} matches were unexpectedly found for "{anno.path}". Taking only the first...')

        match = matches[0]
        gold = anno.union(match)
        save_gold_file(out_dir, gold)

    # Check second annotator
    for anno in anno2:

        # Find matching Brat file in annotator 1
        matches = [brat for brat in anno1 if brat.path == anno.path]

        # If none, only the second annotator has this file and
        # it has not been processed, so save as gold.
        if len(matches) == 0:
            print(f'File "{anno.path}" was only present in the second annotator''s directory. Saving single annotation file without union...')
            save_gold_file(out_dir, anno)
    
union()