import re
import fitz
import os
from OpenTRT import redact_file
import argparse

def main():
    parser = argparse.ArgumentParser(description="Redact a PDF file")
    parser.add_argument('file', help="PDF file to be redacted")
    parser.add_argument('-n', '--num', help="number of (randomly) selected charachter sequences to redact", default=1, type=int)
    parser.add_argument('--input', nargs='+', type=str, help="charachter sequences to redact", default=[])
    parser.add_argument('mode', choices=['replace', "white"], help="Either add a replacement value [x] ('replace') or do not replace redacted values ('white')")
    parser.add_argument('-m', '--metadata',help="Search (xml) metadata for to-be-redacted values.", action='store_true')
    parser.add_argument('-s', '--save_steps', help="Save intermediate steps in PDF documents.", action='store_true')
    args = parser.parse_args()

    file = args.file
    input = args.input
    metadata = args.metadata
    num = args.num
    save_step = args.save_steps
    mode = args.mode
    redact_file(file, num=num, mode=mode, input=input, save_steps=save_step)

    """
    TODO:
    1) create way to select what to redact (file->annotation->redact)
    2) Multiple inputs for char. seqs.
    3) GUI
    4) Documentation
    """

# Using the special variable
# __name__
if __name__=="__main__":
    main()