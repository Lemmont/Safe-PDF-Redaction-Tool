import re
import fitz
import os
from DocumentRedactor import DocumentRedactor, redact_file

def pdf_checker(file):
    doc = fitz.Document(file, filetype="pdf")
    metadata = doc.metadata
    producer = doc.metadata['producer']
    creator = doc.metadata['creator']
    #print(metadata)
    if producer == "":
        print(file, creator)
    else:
        print(file, producer)


def main():
    """
    Example

    steps:
        for each page:
            read annotations/boxes/selected text
            retrieve text in boxes
            get cords/bounding box of text
            remove annots

            get lines of page
            get word of page

            add redact annots to page
            apply redactions

            get lines of page
            get word of page

            determine what to insert
            insert new text
            add white space before and after

            get lines of page
            get word of page

            remove white spaces
    """
    os.chdir('/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/src/test_cases')
    print(os.getcwd())
    files = os.listdir()
    for file in files:
        pdf_checker(file)

    #redact_example()


    # redact a file, save intermediate steps
    redact_file("./noannot.pdf")

# Using the special variable
# __name__
if __name__=="__main__":
    main()