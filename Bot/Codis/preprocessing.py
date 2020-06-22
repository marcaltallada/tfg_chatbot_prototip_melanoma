"""
This script generates a "data.json" file.
"""

import spacy
import csv
import os
import argparse
import json
from utils import get_keywords

nlp = spacy.load('en_core_web_lg')


def generate_data(files):
    """given a list of files, returns ..."""
    data = []
    current_ids = 0
    for file in files:
        text = open(file,'r').read()
        doc = nlp(text)
        for i, phrase in enumerate(doc.sents, current_ids):
            phrase = str(phrase)
            if ('\n' in phrase[:-2]):
                continue
            keywords = get_keywords(phrase)
            if len(keywords) > 3:
                data.append({"sentence": phrase,
                            "keywords": keywords,
                            "source": os.path.basename(file)})
                current_ids += 1
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( 'dir', action = 'store', type = str, help = 'Directory where the sources are stored.' )
    args = parser.parse_args()
    files = os.listdir(args.dir)
    files_path = [args.dir + '/' + f for f in files]
    generate_data(files_path)
