# tests/test_main.py

import os
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import fitz
from OpenTRT import RedactFile
from OpenTRT import DocumentRedactor


punctuation_pattern = r'[.,?"\'!]'

def pdf_checker(file):
    doc = fitz.Document(file, filetype="pdf")
    producer = doc.metadata['producer']
    creator = doc.metadata['creator']
    if producer == "":
        return creator
    else:
        return producer

class ValidateCustomRedactions(unittest.TestCase):
    """
    Unit tests for validating custom redactions in a PDF document.

    Test Cases:
    - 'test_1_simple_1': Validates redaction process with a simple test case.

    Test Environment:
    - The tests utilize the 'unittest' framework.

    Note: Ensure proper setup and cleanup for temporary files if required by the test cases.
    """
    def setUp(self):
        test = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        os.chdir(test)

    def validate_redaction(self, file, num, input=[], metadata=False, path=None):
        prefix = str(file).split("/")[-1].split(".")[0]
        # File before redaction
        origin = pdf_checker(file)
        redactor1 = DocumentRedactor.DocumentInterpreter(file)
        old = redactor1.get_words()

        redactions = RedactFile.redact_file(file, num=4, input=[], mode="replace", metadata=metadata, pos_adj_changed=True, save_steps=False)

        redactor2 = DocumentRedactor.DocumentInterpreter(prefix + "-redacted.pdf")
        new = redactor2.get_words()

        q = 0
        red_cnt = 0
        redaction_list_per_page = {}
        for i in redactions:
            for j in redactions[i]:
                red_cnt += 1
                if q in redaction_list_per_page:
                    redaction_list_per_page[q].append(j)
                else:
                    redaction_list_per_page[q] = [j]
            q += 1

        words = []
        total_edit_distance = 0
        for page in old:

            edit_distance = 0
            old_words = old[page]
            new_words = new[page]
            temp = 0
            for i in range(0, len(old_words)):

                # Last word has been redacted
                if i - edit_distance >= len(new_words):
                   if old_words[i][4] != new_words[i-edit_distance - 1][4] or new_words[i-edit_distance - 1][4] not in old_words[i][4]:

                        edit_distance += 1
                        words.append(old_words[i][4])

                elif old_words[i][4] != new_words[i-edit_distance][4] or new_words[i-edit_distance][4] not in old_words[i][4]:
                    edit_distance += 1
                    words.append(old_words[i][4])

            total_edit_distance += edit_distance

        # check if operations were correct
        self.assertEqual(total_edit_distance, red_cnt, f"FAILED {origin}, {prefix}: edit distance is not equal to the amount of redactions!")
        self.assertEqual(len(words), red_cnt, f"FAILED {origin}, {prefix}: Amount of words labelled as removed in the original is not equal to the amount of given redactions")

        for i in redactions:
            for j in redactions[i]:
                # print(j[4])
                words.remove(j[4])

        self.assertEqual(len(words), 0, f"FAILED {origin}, {prefix}: One or more of the labelled words was/were not part of the given redactions!")
        print(origin, prefix)


    def test_1_simple(self):
        """
            Validate redaction for simple PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'simple_pdf'

        os.chdir(Path(__file__).parent)
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    #print(p, "ok", os.getcwd())
                    self.validate_redaction(p, num=1, metadata=True, path='/results/text_removal/simple')

    def test_2_medium(self):
        """
            Validate redaction for moderate complex PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'medium_pdf'
        os.chdir(Path(__file__).parent)
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                    self.validate_redaction(p, num=1, metadata=True, path='/results/text_removal/medium')

    def test_hard(self):
        """
            Validate redaction for difficult PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'hard_pdf'
        os.chdir(Path(__file__).parent)
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, num=1, metadata=True)

    def test_wild(self):
        """
            Validate redaction for difficult PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'wild'
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, num=1, metadata=True)

    def test_edge(self):
        """
            Validate redaction for difficult PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'edge_pdf'
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, num=1, metadata=True)

    # def test_metadata(self):
    #     for p in Path("./simple_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    #     for p in Path("./medium_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    #     for p in Path("./hard_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    #     for p in Path("./edge_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    def tearDown(self):
        os.chdir(os.path.join(os.getcwd(), '../../..'))

def results():
    f = open("res.txt", "r")
    lines = f.readlines()
    print(lines)


if __name__ == '__main__':
    unittest.main()