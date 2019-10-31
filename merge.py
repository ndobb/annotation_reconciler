import os
import sys
import shutil
from bratmerge.brat_file import BratFile

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
    for row in file.rows:
        f.write(f'{row.to_string()}\n')
    f.close()

def prep(dir_name: str):
    currDir = os.getcwd()

    # Get annotations
    syst = get_brat_objects(os.path.join(currDir, "input", "student"))
    i2b2 = get_brat_objects(os.path.join(currDir, "input", "i2b2"))

    # Prep output directory
    out_dir = os.path.join(currDir, "output", dir_name)
    make_clean_dir(out_dir)

    return out_dir, syst, i2b2

def log_event(path, event_text):
    sys.stdout.write(f'{{ File: "{os.path.basename(path)}", Event: "{event_text}..." }}')
    sys.stdout.write('\n')

def merge_annotations():
    out_dir, syst, i2b2 = prep("merge")

    # Check system notes
    for anno in syst:

        # Find matching Brat file in i2b2
        matches = [brat for brat in i2b2 if brat.path == anno.path]
        cnt = len(matches)

        if cnt == 0:
            log_event(anno.path, 'No matches found for file. Skipping')
            continue

        if cnt > 1:
            log_event(anno.path, f'{cnt} matching files were unexpectedly found. Taking only first')

        match = matches[0]
        gold = anno.merge(match)
        save_gold_file(out_dir, gold)

    # Check i2b2
    for anno in i2b2:

        # Find matching Brat file in annotator 1
        matches = [brat for brat in syst if brat.path == anno.path]

        # If none, only the second annotator has this file and
        # it has not been processed, so save as gold.
        if len(matches) == 0:
            sys.stdout.write(f'File: "{anno.path}", Event: "File was only present in i2b2 directory. Saving single annotation file without merge..."')
            save_gold_file(out_dir, anno)
    
merge_annotations()