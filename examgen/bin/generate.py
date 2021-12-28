import argparse
import random

from examgen import SourceDocument
from examgen import named_ents


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=str,
                    help='Filepath of text file to process')

args = parser.parse_args()
print("Reading {}".format(args.source_file))
with open(args.source_file, 'r') as f:
    doc = SourceDocument(f)

question = None
while question is None:
    question = named_ents.sample(doc)
print(question)
print(question.answer_key())