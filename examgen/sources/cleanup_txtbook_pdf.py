"""
Utility for cleaning up PDFs from textbooks
"""
import argparse
from examgen.sources.cleanup import *

parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=str, help="Filepath to PDF to process")
parser.add_argument('target_file', type=str, default="processed.txt",
                    help="Filepath to text output")

args = parser.parse_args()

filter_fns = [
    filter_pagenums, filter_heading, filter_singletoks, filter_partheading
]

with open(args.source_file, 'r') as f:
    with open(args.target_file, 'w') as f_out:
        for line in f:
            for filter_fn in filter_fns:
                line = filter_fn(line)
                if line is None:
                    break
            if line is not None:
                f_out.write(line+"\n")