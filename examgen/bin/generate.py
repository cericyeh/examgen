import argparse
import random

from examgen import SourceDocument
from examgen import named_ents
from examgen.named_ents import PERSON, ORG, GPE, LOC, NORP


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=str,
                    help='Filepath of text file to process')
parser.add_argument('--questions_file', type=str,
                    default='questions.txt',
                    help='Filepath to write questions to')
parser.add_argument('--key_file', type=str,
                    default='answer_key.txt',
                    help="Filepath to write answer key to")
parser.add_argument('--num_questions', type=int,
                    default=50,
                    help="Number of questions to generate")
args = parser.parse_args()
print("Reading {}".format(args.source_file))
with open(args.source_file, 'r') as f:
    doc = SourceDocument(f)

questions = []
for idx in range(args.num_questions):
    question = None
    while question is None:
        ent_type = random.choice([PERSON, ORG, GPE, LOC, NORP])
        question = named_ents.sample(doc, ent_type)
    questions.append(question)

with open(args.questions_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.question(idx=idx + 1))
        f.write("\n\n")

with open(args.key_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.answer_key(idx=idx + 1))
        f.write("\n\n")