from tqdm import tqdm
import random
import spacy
import re
import abc
nlp = spacy.load('en_core_web_sm')
BLANK = "_____"

CIT_PATTERN = "\\[\\d+\\]"

class SourceDocument:
    def __init__(self, f, total_lines=None):
        """
        Preprocesses the input text reader, running NLP analysis
        over each line (segment).  Entities are cached.
        To avoid confusing the sentence splitter, Wikipedia-style references
        are excised
        :param f: File input reader
        """
        self.segments = []
        self.all_sents = []
        for line in tqdm(f, total=total_lines):
            line = re.sub(CIT_PATTERN, "", line.strip())
            segment = nlp(line)
            self.segments.append(segment)
            self.all_sents.extend(segment.sents)
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

def read(fpath):
    with open(fpath, 'r') as f:
        num_lines = 0
        for _ in f:
            num_lines += 1
    with open(fpath, 'r') as f:
        doc = SourceDocument(f, num_lines)
    return doc


class Question:
    @abc.abstractmethod
    def get_gold(self):
        pass

    @abc.abstractmethod
    def get_question(self):
        pass

    @abc.abstractmethod
    def get_choices(self):
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
        ret = "{} (choose one)\n".format(self.question_txt)
        for idx, choice in enumerate(self.choices):
            ret += "\t{}: {}\n".format(idx, choice)
        return ret



