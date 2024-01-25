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
        print("SETUP")
        test = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        os.chdir(test)
        print("CURRENT DIR:", os.getcwd())

    def validate_redaction(self, file, num, input=[], metadata=False, path=None):
        prefix = str(file).split("/")[-1].split(".")[0]
        # File before redaction
        redactor1 = DocumentRedactor.DocumentInterpreter(file)
        old = redactor1.get_words()
        orginal = os.getcwd()
        temp = pdf_checker(file)
        redactions = RedactFile.redact_file(file, num, input, mode="white", metadata=metadata, pos_adj_changed=True, path=path)

        os.chdir
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
        self.assertEqual(total_edit_distance, red_cnt, "FAILED: edit distance is not equal to the amount of redactions!")
        self.assertEqual(len(words), red_cnt, "FAILED: Amount of words labelled as removed in the original is not equal to the amount of given redactions")

        for i in redactions:
            for j in redactions[i]:
                # print(j[4])
                words.remove(j[4])

        self.assertEqual(len(words), 0, "FAILED: One or more of the labelled words was/were not part of the given redactions!")

    def validate_metadata(self, file, redactions, num=1, input=[]):
        prefix = str(file).split("/")[-1].split(".")[0]

        # Step 1: Retrieve metadata before and after redaction.
        redactor1 = DocumentRedactor(file)
        old_metadata = redactor1.get_metadata()
        redactions = RedactFile.redact_file(file, num, input, metadata=True)
        redactor2 = DocumentRedactor(prefix + "-redacted.pdf")

        old_xml_metadata = ET.fromstring(redactor1.doc.get_xml_metadata())
        new_metadata = redactor2.get_metadata()
        new_xml_metadata = ET.fromstring(redactor2.doc.get_xml_metadata())


        # Step 2: Compare metadata values for redacted words and input strings.
        to_be_redacted = set()
        for i in redactions:
            for j in redactions[i]:
                to_be_redacted.add(j[4])
        for i in input:
            to_be_redacted.add(i)

        for j in to_be_redacted:
            for i in old_metadata:
                old_val = old_metadata[i]
                new_val = new_metadata[i]

                # Step 3: Check if redacted values in metadata match the expected redacted format "[x]".
                if old_val is not None and new_val is not None and old_val != new_val:
                    self.assertEqual(str(old_val).replace(j, "[x]"), new_val,
                                    f"'{str(old_val).replace(j, '[x]')}' is not equal to {new_val}. "
                                    f"It seems that redaction of {j} was not performed successfully")

        # Step 4: Compare XML metadata values for redacted words.
        xml_data = {}
        for elem in old_xml_metadata.iter():
            for i in to_be_redacted:
                if elem.text is not None:
                    val = elem.text.replace(i, "[x]")
                else:
                    val = None

                if val in xml_data:
                    xml_data[val] += 1
                else:
                    xml_data[val] = 1

        for elem in new_xml_metadata.iter():
            # Step 5: Raise AssertionError if any of the validation checks fail.
            if elem.text in xml_data:
                with self.subTest(elem.text):
                    self.assertNotEqual(xml_data[elem.text], 0, "Assertion failed: Redacted XML metadata not found.")
                    xml_data[elem.text] -= 1
            else:
                self.assertTrue(elem.text in xml_data,
                                f"'{elem.text}' was not in the original file. "
                                f"It seems it has been added to the metadata while redacting the file.")

    def test_1_simple(self):
        """
            Validate redaction for simple PDF documents.
        """
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'simple_pdf'

        print(pdf_directory)
        os.chdir(Path(__file__).parent)
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    #print(p, "ok", os.getcwd())
                    self.validate_redaction(p, num=3, metadata=True, path='/results/text_removal/simple')

    # def test_2_medium(self):
    #     """
    #         Validate redaction for moderate complex PDF documents.
    #     """
    #     # Get the current directory of the test file
    #     test_file_directory = Path(__file__).parent
    #     # Construct the path to the "corpus/simple_pdf" directory
    #     pdf_directory = test_file_directory / 'corpus' / 'medium_pdf'
    #     print(pdf_directory, "ok2")
    #     os.chdir(Path(__file__).parent)
    #     for p in pdf_directory.glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 print(p, "ok", os.getcwd())
    #                 #self.validate_redaction(p, num=3, metadata=True, path='/results/text_removal/medium')

    # def test_hard(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./hard_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=3, metadata=True)

    # def test_wild(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./wild").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=3, metadata=True)

    # def test_edge(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./edge_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

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