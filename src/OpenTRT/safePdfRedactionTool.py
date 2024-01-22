import re
import fitz
import os
from SafeRedaction import DocumentRedactor, RedactionSelector, redact_file


def main():
    """
    """
    # print(os.getcwd())
    # files = os.listdir()
    # for file in files:
    #     pdf_checker(file)

    redact_file("./../test_cases/simple_pdf/simple2.pdf", num=2, mode="replace", display=True, pos_adj_changed=True)

# Using the special variable
# __name__
if __name__=="__main__":
    main()