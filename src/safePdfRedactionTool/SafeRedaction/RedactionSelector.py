from typing import List, Dict
from SafeRedaction import DocumentRedactor
import random
import fitz

class RedactionSelector:
    def __init__(self, document_redactor):
        self.redactor: DocumentRedactor.DocumentRedactor = document_redactor
        self.redactions: Dict = None

    def __str__(self) -> str:
        msg = "--- GENERATED REDACTIONS PER PAGE ----\n\n"
        if self.redactions != None or self.redactions != {}:
            for i in self.redactions:
                msg += str(i) + "\n--- REDACTIONS ----\n"
                for j in self.redactions[i]:
                    msg += "> " + str(j) + "\n"

                msg += "\n"
        else:
            msg = "no redactions"

        return msg

    def select_redactions(self, num=1, input=[]):
        pages = self.redactor.pages

        redactions = {}
        if input != []:
            redactions = _select_redaction_based_on_input(pages, input[0])
        else:
            redactions = _generate_redactions_per_page(self.redactor, pages, num)

        self.redactions = redactions
        return redactions


def _select_redaction_based_on_input(pages: List[fitz.Page], input):
    words_selected = {}
    for page in pages:
        selected = []
        res = page.search_for(input)
        for r in res:
            text = page.get_text("words", clip=r, sort=True)
            #print(r, text)
            for t in text:
                selected.append(t)

        words_selected[page] = selected

    return words_selected


def _select_multiple_redactions_example(words, num):
        words_list = []
        b = []
        while len(b) != num:
            for i in range(random.randint(1, num)):
                a = random.randint(0, len(words) - 1)
                if a not in b:
                    b.append(a)

                if len(b) == num:
                    break

        b.sort()
        for j in b:
            words_list.append(words[j])

        return words_list

def _generate_redactions_per_page(redactor: DocumentRedactor, pages, num):
        redactions_per_page = {}
        for page in pages:
            page.clean_contents()
            words = page.get_text("words", sort=True)
            redactions = _select_multiple_redactions_example(words, num)
            redactions_per_page[page] = redactions

        return redactions_per_page
