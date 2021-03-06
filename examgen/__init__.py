from tqdm import tqdm
import random
import spacy
import re
import abc

nlp = spacy.load('en_core_web_sm')
BLANK = "_____"

CIT_PATTERN = "\\[\\d+\\]"
CIT_PATTERN2 = "”\\d+"

class SourceDocument:
    def __init__(self, f, total_lines=None):
        """
        Preprocesses the input text reader, running NLP analysis
        over each line (segment).  Entities are cached.
        To avoid confusing the sentence splitter, Wikipedia-style references
        are excised
        :param f: File input reader
        """
        self.segment_txts = []
        self.all_sents = []
        all_lines = f.readlines()
        # Read in and repair broken lines.  Segments
        # are delimited by empty lines
        curr_seg = []
        for line in tqdm(all_lines):
            line = line.strip()
            if len(line) == 0:
                if len(curr_seg) > 0:
                    self.segment_txts.append(curr_seg)
                    curr_seg = []
            else:
                curr_seg.append(line)
        if len(curr_seg) > 0:
            self.segment_txts.append(curr_seg)
        self.segments = []
        for segment_lines in tqdm(self.segment_txts):
            # Go through each segment, collapsing continuations together.
            segment_txt = ""
            is_continuation = False
            # TODO: Optimize line continuation logic
            for line in segment_lines:
                line = line.strip()
                if is_continuation:
                    if line.endswith("-"):
                        segment_txt += line[:-1]
                        is_continuation = True
                    else:
                        segment_txt += line
                        is_continuation = False
                else:
                    if line.endswith("-"):
                        segment_txt += " {}".format(line[:-1])
                        is_continuation = True
                    else:
                        segment_txt += " {}".format(line)
                        is_continuation = False
            orig_segment_txt = segment_txt
            segment_txt = re.sub(CIT_PATTERN, " ", segment_txt.strip())
            segment_txt = re.sub(CIT_PATTERN2, "”", segment_txt.strip())

            segment_doc = nlp(segment_txt)

            self.segments.append(segment_doc)
            for sent in segment_doc.sents:
                has_verb = False
                for tok in sent:
                    if tok.tag_.startswith("V"):
                        has_verb = True
                if not(has_verb):
                    continue
                if len(sent) <= 5:
                    # Presume sentences of 5 tokens or less are not valid sentences.
                    continue
                self.all_sents.append(sent)
        # Grab all entities
        self.all_ents = []
        for segment in self.segments:
            self.all_ents.extend(segment.ents)

    def find_segment(self, sentence):
        """ Given a sentence drawn from this document,
        returns the matching segment"""
        for idx, segment in enumerate(self.segments):
            if sentence.text in segment.text:
                return segment
        return None

    def sample_sentence(self):
        """
        Randomly chooses a sentence, returning the matching segment
        :return:
        """
        sentence = random.choice(self.all_sents)
        segment = self.find_segment(sentence)
        return sentence, segment

def read_doc(fpath):
    with open(fpath, 'r') as f:
        num_lines = 0
        for _ in f:
            num_lines += 1
    with open(fpath, 'r') as f:
        doc = SourceDocument(f, num_lines)
    return doc


class Question:
    @abc.abstractmethod
    def get_gold(self) -> str:
        pass

    @abc.abstractmethod
    def get_question(self) -> str:
        pass

    @abc.abstractmethod
    def get_choices(self) -> list[str]:
        pass

    def question(self, idx=None):
        if idx is not None:
            ret = "{}) {}\n".format(idx, self.question_txt)
        else:
            ret = "{}\n".format(self.question_txt)
        for idx, choice in enumerate(self.choices):
            ret += "\t{}: {}\n".format(idx, choice)
        return ret

    def answer_key(self, idx=None):
        if idx is not None:
            ret = "{}) {}\n".format(idx, self.question_txt)
        else:
            ret = "{}\n".format(self.question_txt)
        golds = self.get_gold()
        ret += "ANSWER: {}\n".format(golds)
        for idx, choice in enumerate(self.choices):
            if isinstance(golds, list) or isinstance(golds, set):
                is_gold = choice in golds
            else:
                is_gold = choice == golds
            if is_gold:
                ret += "\t{}: ***{}***\n".format(idx, choice)
            else:
                ret += "\t{}: {}\n".format(idx, choice)
        return ret


class MultipleChoiceQuestion(Question):
    def __init__(self, sentence:str, gold:str, confounders:list):
        assert gold in sentence
        question_txt = sentence.replace(gold, BLANK) + "\nChoose One"
        self.gold, self.question_txt = gold, question_txt
        assert gold not in confounders
        self.choices = [gold] + confounders
        random.shuffle(self.choices)
        self.gold_idx = self.choices.index(self.gold)

    def get_question(self):
        return self.question_txt

    def get_choices(self):
        return self.choices

    def get_gold(self):
        return self.gold

    def __str__(self):
        ret = "{}\nChoose one:\n".format(self.question_txt)
        for idx, choice in enumerate(self.choices):
            ret += "\t{}: {}\n".format(idx, choice)
        return ret



