import random
from examgen import SourceDocument, MultipleChoiceQuestion
import numpy as np

"""
Constructs questions using named entities.
"""

PERSON="PERSON"
DATE="DATE"
ORG="ORG"
GPE="GPE"
LOC="LOC"
NORP="NORP"

def _valid_sentence(sentence):
    txt = sentence.text.strip()
    if txt[0] == '(' and txt[1] == ')':
        return False
    if txt[-1] == '?':
        return False
    has_verb = False
    for tok in sentence:
        if tok.tag_.startswith("V"):
            has_verb = True
    if not(has_verb):
        return False
    return True

def sample(doc:SourceDocument, ent_type=PERSON, num_choices=5,
           min_sent_tokens=5,
           max_tries=100):
    """
    Given a sentence and the source document it was pulled from,
    samples a multiple choice question.  For multiword entities, uses
    the root word to identify the type.
    :param sentence:
    :param doc:
    :param num_choices: Number of choices total
    :param min_sent_tokens: Minimum length of sentence to use
    :return:
    """
    sentence = None
    num_tries = 0
    while (sentence is None or len(sentence) < min_sent_tokens) and num_tries <= max_tries:
        sentence, segment = doc.sample_sentence()
        if not(_valid_sentence(sentence)):
            sentence = None

    sent_ents = sentence.ents
    segment_ents = segment.ents
    valid_sent_ents = [x for x in sent_ents if x[-1].ent_type_ == ent_type]
    if len(valid_sent_ents) == 0:
        return None
    selected_ent = random.choice(valid_sent_ents)
    local_confounders = set([x.text for x in segment_ents
                         if x[-1].ent_type_ == ent_type and
                             x.text != selected_ent.text])
    global_confounders = set([x.text for x in doc.all_ents
                         if x[-1].ent_type_ == ent_type and
                              x.text != selected_ent.text and
                              x.text not in local_confounders])
    weights = [10 for _ in range(len(local_confounders))]
    weights.extend([1 for _ in range(len(global_confounders))])
    weights = np.array(weights) / np.sum(weights)
    all_confounders = list(local_confounders) + list(global_confounders)
    confounders = list(np.random.choice(all_confounders, size=num_choices,
                                   replace=False, p=weights))
    question = MultipleChoiceQuestion(sentence.text, selected_ent.text, confounders)
    return question
    # Select N confounders from local segment, then from global
