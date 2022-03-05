from tqdm import tqdm
from spacy.matcher import DependencyMatcher
from examgen import nlp
from examgen import SourceDocument
from examgen.relations import Relation, StubToken


""""
Take copulas and construct questions from them.
"""

ISA_RELN = "is-a"
COPULA_ANCHOR = "copula_anchor"
COPULA_SUBJECT = "copula_subject"
COPULA_OBJECT = "copula_object"

copula_pattern = [
    # Anchor token: Lemma 'is'
    {
        "RIGHT_ID": COPULA_ANCHOR,
        "RIGHT_ATTRS": {"LEMMA": "be"}
    },
    # Subject
    { "LEFT_ID": "copula_anchor",
      "REL_OP": ">",
      "RIGHT_ID": COPULA_SUBJECT,
      "RIGHT_ATTRS": {"DEP": "nsubj"}
    },
    { "LEFT_ID": "copula_anchor",
      "REL_OP": ">",
      "RIGHT_ID": COPULA_OBJECT,
      "RIGHT_ATTRS": {"DEP": "attr"},
    },
]

APPOS_ANCHOR = "appos_anchor"

appos_pattern1 = [
    # Subject
    {
      "RIGHT_ID": COPULA_SUBJECT,
      "RIGHT_ATTRS": {"TAG": "NNP"}
    },
    { "LEFT_ID": COPULA_SUBJECT,
      "REL_OP": ">",
      "RIGHT_ID": COPULA_OBJECT,
      "RIGHT_ATTRS": {"DEP": "appos"},
    }
]

appos_pattern2 = [
    # Subject
    {
      "RIGHT_ID": COPULA_SUBJECT,
      "RIGHT_ATTRS": {"TAG": "NN"}
    },
    { "LEFT_ID": COPULA_SUBJECT,
      "REL_OP": ">",
      "RIGHT_ID": COPULA_OBJECT,
      "RIGHT_ATTRS": {"DEP": "appos"},
    }
]

copula_depmatcher = matcher = DependencyMatcher(nlp.vocab)
copula_depmatcher.add("copula", [copula_pattern])

appos_depmatcher = matcher = DependencyMatcher(nlp.vocab)
appos_depmatcher.add("appos", [appos_pattern1, appos_pattern2])


def extract_copulas(doc:SourceDocument):
    # First select candidate
    copula_matches = []
    for segment in tqdm(doc.segments):
        matches = copula_depmatcher(segment)
        for match_id, token_ids in matches:
            subject_tok, dobj_tok, copula_anchor = None, None, None
            for pidx in range(len(token_ids)):
                pattern_id = copula_pattern[pidx]['RIGHT_ID']
                tok_id = token_ids[pidx]
                if pattern_id == COPULA_SUBJECT:
                    subject_tok = segment[tok_id]
                elif pattern_id == COPULA_OBJECT:
                    dobj_tok = segment[tok_id]
                elif pattern_id == COPULA_ANCHOR:
                    copula_anchor = segment[tok_id]
                else:
                    raise Exception("Copula processing: Unknown pattern ID={}".format(pattern_id))
            sanity_flag = subject_tok is not None and \
                dobj_tok is not None and \
                copula_anchor is not None
            assert subject_tok is not None and \
                dobj_tok is not None and \
                copula_anchor is not None
            copula_matches.append(Relation(copula_anchor, subject_tok, dobj_tok, ISA_RELN))
    return copula_matches


def extract_appositives(doc:SourceDocument):
    # First select candidate
    copula_matches = []
    for segment in tqdm(doc.segments):
        matches = appos_depmatcher(segment)
        for match_id, token_ids in matches:
            subject_tok, dobj_tok = None, None
            for pidx in range(len(token_ids)):
                pattern_id = appos_pattern1[pidx]['RIGHT_ID']
                tok_id = token_ids[pidx]
                if pattern_id == COPULA_SUBJECT:
                    subject_tok = segment[tok_id]
                elif pattern_id == COPULA_OBJECT:
                    dobj_tok = segment[tok_id]
                else:
                    raise Exception("Appostive processing: Unknown pattern ID={}".format(pattern_id))
            assert subject_tok is not None and \
                dobj_tok is not None
            # Sanity checks: Ensure either the subject or object is a proper noun.  If not, then
            # this is likely not a good relation for question generation
            if not(subject_tok.tag_ == "NNP" or dobj_tok.tag_ == "NNP"):
                continue
            if subject_tok.tag_ == "CD" or dobj_tok.tag_ == "CD":
                continue  # This is likley a date
            reln = Relation(StubToken("be"), subject_tok, dobj_tok, ISA_RELN)
            if len(reln.get_subj_toks()) == 1 and len(reln.get_obj_toks()) == 1:
                # Likley to be spurious match
                continue
            copula_matches.append(reln)
    return copula_matches
