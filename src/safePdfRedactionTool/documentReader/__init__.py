import re
import fitz
from typing import List

class DocumentReader:
    """
        A class that reads the internals of a PDF document

        add more info
    """
    def __init__(self, document):
        self.doc: fitz.Document = fitz.open(document, filetype="pdf")


    def get_pages(self):
        """
            Get pages of document
        """
        return [page for page in self.doc]

    def get_page_dimensions(self, page: fitz.Page):
        """
            Get cropbox/dimensions of page
        """
        cropbox = page.cropbox
        return (cropbox.x1, cropbox.y1)

    def get_page_contents(self, page: fitz.Page):
        """
            returns xref, lines and words of page.
        """
        xref = page.get_contents()[0]
        lines = page.read_contents().splitlines()
        words = page.get_text("words")
        return (xref, lines, words)

    def get_redact_annots(self, page: fitz.Page):
        pass

    def get_words_in_annot(self, annot: fitz.Rect):
        pass

    def get_word_bbox(self, word: str):
        pass

    def get_to_be_repositioned_words(self, page_height, lines, first_redaction: fitz.Rect):
        to_be_repositioned = []
        for i in range(len(lines)):
            if lines[i].endswith(b"Tm"):
                string_line = lines[i].split()
                x = float(string_line[4])
                y = page_height - float(string_line[5])
                if x >= first_redaction[0] and  y >= first_redaction[1] and y <= first_redaction[3]:
                    to_be_repositioned.append((lines[i], i))

        return to_be_repositioned

