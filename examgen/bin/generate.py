import argparse
import random

from examgen import SourceDocument
from examgen import named_ents


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=str,
                    help='Filepath of text file to process')
parser.add_argument('--questions_file', type=str,
                    default='questions.txt',
                    help='Filepath to write questions to')
parser.add_argument('--key_file', type=str,
                    default='answer_key.txt',
                    help="Filepath to write answer key to")
args = parser.parse_args()
print("Reading {}".format(args.source_file))
with open(args.source_file, 'r') as f:
    doc = SourceDocument(f)

num_questions = 30
questions = []
for idx in range(num_questions):
    question = None
    while question is None:
        question = named_ents.sample(doc)
    questions.append(question)

with open(args.questions_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.question(idx=idx))
        f.write("\n\n")

with open(args.key_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.answer_key(idx=idx))
        f.write("\n\n")