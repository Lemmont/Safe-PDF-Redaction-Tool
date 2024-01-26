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
    def validate_metadata(self, file, redactions, num=1, input=[]):
        prefix = str(file).split("/")[-1].split(".")[0]

        # Step 1: Retrieve metadata before and after redaction.
        redactor1 = DocumentRedactor.DocumentInterpreter(file)
        old_metadata = redactor1.get_metadata()
        redactions = RedactFile.redact_file(file, num, input, metadata=True, save_steps=False)
        redactor2 = DocumentRedactor.DocumentInterpreter(prefix + "-redacted.pdf")

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


    def test_metadata(self):
        # Get the current directory of the test file
        test_file_directory = Path(__file__).parent
        # Construct the path to the "corpus/simple_pdf" directory
        pdf_directory = test_file_directory / 'corpus' / 'simple_pdf'
        for p in pdf_directory.glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        for p in Path("./medium_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        # for p in Path("./hard_pdf").glob('*.pdf'):
        #     with self.subTest(p=p):
        #         if p != "temp.pdf":
        #             self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

        # for p in Path("./edge_pdf").glob('*.pdf'):
        #     with self.subTest(p=p):
        #         if p != "temp.pdf":
        #             self.validate_metadata(p, redactions={}, num=1, input=["Lennaert Feijtes"])

    def tearDown(self):
        os.chdir(os.path.join(os.getcwd(), '../../..'))

def results():
    f = open("res.txt", "r")
    lines = f.readlines()
    print(lines)


if __name__ == '__main__':
    unittest.main()