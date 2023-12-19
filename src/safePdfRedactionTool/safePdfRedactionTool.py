import re
import fitz
import os
from SafeRedaction import DocumentRedactor, RedactionSelector, redact_file

# def pdf_checker(file):
#     doc = fitz.Document(file, filetype="pdf")
#     metadata = doc.metadata
#     producer = doc.metadata['producer']
#     creator = doc.metadata['creator']
#     #print(metadata)
#     if producer == "":
#         print(file, creator)
#     else:
#         print(file, producer)


def main():
    """
    """
    # print(os.getcwd())
    # files = os.listdir()
    # for file in files:
    #     pdf_checker(file)

    redact_file("./../test_cases/simple4.pdf", num=5, mode="replace")

# Using the special variable
# __name__
if __name__=="__main__":
    main()