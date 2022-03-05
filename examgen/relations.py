from spacy.tokens.token import Token
from .named_ents import PERSON, NORP, GPE, ORG

ACTOR_NERS = set([PERSON, NORP, GPE, ORG])

def _span2txt(span):
    """ Converts the given Token span into text.  Removes
    trailing and bracketing parens, which may accidentally be included into NNPs"""
    txt = " ".join([t.text for t in span]).strip()
    if txt.endswith('('):
        txt = txt[:-1]
    elif txt.startswith('(') and txt.endswith(')'):
        txt = txt[1:-1]
    elif txt.endswith(')'):
        txt = txt[:-1]

    return txt

class StubToken():
    def __init__(self, text):
        self.text = text


class Relation:
    def __init__(self, pred, arg1:Token, arg2:Token, reln_type:str):
        self.pred, self.arg1, self.arg2 = pred, arg1, arg2
        self.reln_type = reln_type

    def get_pred(self):
        return self.pred.text

    def get_subj(self) -> str:
        return _span2txt(_traversal(self.arg1))

    def get_subj_toks(self) -> str:
        return _traversal(self.arg1)

    def get_obj(self) -> str:
        return _span2txt(_traversal(self.arg2))

    def get_obj_toks(self) -> str:
        return _traversal(self.arg2)

    def get_subj_ner(self) -> str:
        return self.arg1.ent_type_

    def get_obj_ner(self) -> str:
        return self.arg2.ent_type_

    def __str__(self):
        return "({}: {}\n\t{}\n\t{}\n)".format(self.reln_type, self.get_pred(),
                                         self.get_subj(), self.get_obj())


def _traversal(tok, num_preps=0):
    """ Traversal with intent to get sensible arg1s and arg2s for relation
    based questions.  Heuristics are,
    - Only one preposition traversed
    - No relative clauses traversed (too long) """
    accum = []
    children = list(tok.children)
    if len(children) == 0:
        return [tok]
    else:
        accum.append(tok)
        for ct in children:
            dep = ct.dep_
            if num_preps == 0 and dep == 'prep':
                accum.extend(_traversal(ct, num_preps = num_preps + 1))
            elif dep != "relcl" and dep != "appos":
                accum.extend(_traversal(ct))
        return sorted(accum, key=lambda x: x.idx)


def organize_by_ent(relns):
    ret = {}
    for reln in relns:
        arg1_ner = reln.get_subj_ner()
        if len(arg1_ner) == 0:
            arg1_ner = "NONE"
        if arg1_ner not in ret:
            ret[arg1_ner] = []
        ret[arg1_ner].append(reln)
    return ret


def filter_valid_arg1s(relns):
    """
    Identifies subset of relations whose arg1s are suitable noun candidates
    :param reln:
    :return:
    """
    ret = []
    for reln in relns:
        subj_txt = reln.get_subj().strip()
        obj_txt = reln.get_obj().strip()

        if subj_txt.endswith(" of"):
            continue

        if subj_txt[-1] in set([":", ",", ";", ".", "-"]) or \
                obj_txt[0].strip() in set([":", ",", ";", ".", "-"]):
            # Subject likely a mis-extraction of a section header followed by description,
            # or a mangled sentence
            continue
        if reln.arg1.tag_.startswith("NN"):
            ret.append(reln)
        elif reln.get_subj_ner() in ACTOR_NERS:
            ret.append(reln)
    return ret