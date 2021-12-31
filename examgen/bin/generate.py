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
# Set the upper limit on sampling tries
MAX_TRIES = 1000
args = parser.parse_args()
print("Reading {}".format(args.source_file))
with open(args.source_file, 'r') as f:
    doc = SourceDocument(f)

questions = []
question_tabu = set()
for idx in range(args.num_questions):
    question = None
    num_tries = 0
    while (question is None) and (num_tries <= MAX_TRIES):
        ent_type = random.choice([PERSON, ORG, GPE, LOC, NORP])
        question = named_ents.sample(doc, ent_type)
        num_tries += 1
        if question is not None and \
                question.get_question() in question_tabu:
            question = None
    if question is not None:
        question_tabu.add(question.get_question())
        questions.append(question)
    else:
        print("Warning, unable to sample new question!")

with open(args.questions_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.question(idx=idx + 1))
        f.write("\n\n")

with open(args.key_file, 'w') as f:
    for idx, question in enumerate(questions):
        f.write(question.answer_key(idx=idx + 1))
        f.write("\n\n")