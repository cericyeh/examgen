"""
Utilities for cleaning up text files, primarily for
dealing with PDFs.

The filter routines accept a line, and either return
a cleaned up version of the line, or None.  If None,
the line is not to be included in the text.
"""
import re

from examgen import nlp

def filter_pagenums(line):
    """
    If the given line starts with a number,
    :param line:
    :return:
    """
    line = line.strip()
    if len(line) > 0 and line[0].isdigit():
        return None
    return line

def filter_heading(line):
    line = line.strip()
    if line.lower().startswith("chapter"):
        return None
    return line

def filter_partheading(line):
    """
    Removes 'part 4 / The New World'
    :param line:
    :return:
    """
    line = line.strip()
    m = re.search("part \d+ \/", line)
    if m:
        return None
    return line

def filter_singletoks(line):
    line = line.strip()
    doc = nlp(line, disable=['parser', 'tagger', 'ner'])
    if len(doc) == 1:
        return None
    return line
