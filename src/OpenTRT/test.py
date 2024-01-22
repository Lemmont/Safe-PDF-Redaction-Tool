import os
import unittest
from OpenTRT import redact_file, DocumentRedactor
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import fitz

punctuation_pattern = r'[.,?"\'!]'

def pdf_checker(file):
    doc = fitz.Document(file, filetype="pdf")
    producer = doc.metadata['producer']
    creator = doc.metadata['creator']
    #print(metadata)
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
        os.chdir('/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/src/test_cases')

    def validate_redaction(self, file, num=1, input=[], metadata=False):
        prefix = str(file).split("/")[-1].split(".")[0]
        # File before redaction
        redactor1 = DocumentRedactor(file)
        old = redactor1.get_words()

        temp = pdf_checker(file)

        f = open("res.txt", "a")
        f.write("[ " + temp + " ] ")
        f.close()

        # Perform redaction
        try:
            f = open("res.txt", "a")
            redactions = redact_file(file, num, input, metadata=metadata, pos_adj_changed=True)
        except:
            f.write(f"{prefix} false error\n")
            f.close()
            return

        # Prepare a dictionary to store redactions per page
        redaction_list_per_page = {}
        q = 0
        for i in redactions:
            for j in redactions[i]:
                if q in redaction_list_per_page:
                    redaction_list_per_page[q].append(j)
                else:
                    redaction_list_per_page[q] = [j]
            q += 1

        # File after redaction
        redactor2 = DocumentRedactor(prefix + "-redacted.pdf")
        new = redactor2.get_words()

        # Validation loop
        redactions_found = {}
        for page in old:
            old_words = old[page]
            new_words = new[page]
            q = 0
            l = 0
            w = 0
            p = 0
            for i in range(0, len(old_words)):
                if i - w >= len(old_words) or i - p + l >= len(new_words):
                    # Ensure not to go beyond the list boundaries
                    break

                if new_words[i - p + l][4] == "[x]":
                    w += 1
                else:
                    if i - w >= len(old_words):
                        break  # Ensure not to go beyond the list boundaries

                    if old_words[i - w][4] != new_words[i - p + l][4]:
                        if i - w >= len(old_words) or q >= len(redaction_list_per_page[page]):
                            break  # Ensure not to go beyond the list boundaries

                        if old_words[i - w][4] != redaction_list_per_page[page][q][4]:
                            # Perform a subTest for more granular test reporting
                            with self.subTest(q=q, i=i, w=w):
                                # Validate that the redacted content matches the expected value
                                if redaction_list_per_page[page][q][4] not in str(old_words[i - w][4]).lower():
                                    f.write(" " + "error\n")
                                    f.close()
                                    return
                                self.assertIn(redaction_list_per_page[page][q][4], str(old_words[i - w][4]).lower(), "Error")

                                # If there are multiple redactions on the page, increment the counter
                                if len(redaction_list_per_page[page]) != 1:
                                    l += 1

                        # If there's only one redaction on the page, increment the counter
                        if len(redaction_list_per_page[page]) <= 1:
                            q += 1

                        # Increment the counter for redactions on the page
                        if len(redaction_list_per_page[page]) > 0:
                            p += 1

            # Count the number of redactions found on the page
            for j in range(0, len(new_words)):
                if re.sub(punctuation_pattern, '', new_words[j][4]) == "[x]":
                    if page in redactions_found:
                        redactions_found[page] += 1
                    else:
                        redactions_found[page] = 1

        # Check if the count of redactions found matches the expected count
        for page in old:
            if page in redaction_list_per_page:
                if redactions_found[page] != len(redaction_list_per_page[page]):
                    f.write(" " + "error\n")
                self.assertEqual(redactions_found[page], len(redaction_list_per_page[page]), f"ERROR: Amount of found redactions ({redactions_found[page]}) is not equal to the actual redactions ({len(redaction_list_per_page[page])})!")

        f.write(" " + "succes\n")
        f.close()

    def validate_metadata(self, file, redactions, num=1, input=[]):
        prefix = str(file).split("/")[-1].split(".")[0]

        # Step 1: Retrieve metadata before and after redaction.
        redactor1 = DocumentRedactor(file)
        old_metadata = redactor1.get_metadata()
        redactions = redact_file(file, num, input, metadata=True)
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

    # def test_simple(self):
    #     """
    #         Validate redaction for simple PDF documents.
    #     """
    #     for p in Path("./simple_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

    # def test_medium(self):
    #     """
    #         Validate redaction for moderate complex PDF documents.
    #     """
    #     for p in Path("./medium_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

    # def test_hard(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./hard_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

    # def test_wild(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./wild").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

    # def test_edge(self):
    #     """
    #         Validate redaction for difficult PDF documents.
    #     """
    #     for p in Path("./edge_pdf").glob('*.pdf'):
    #         with self.subTest(p=p):
    #             if p != "temp.pdf":
    #                 self.validate_redaction(p, num=1, metadata=True)

    def test_metadata(self):
        for p in Path("./simple_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        for p in Path("./medium_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        for p in Path("./hard_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        for p in Path("./edge_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    def tearDown(self):
        pass

def results():
    f = open("res.txt", "r")
    lines = f.readlines()
    print(lines)


if __name__ == '__main__':
    unittest.main()