import os
import unittest
from SafeRedaction import redact_file, DocumentRedactor
import xml.etree.ElementTree as ET
from pathlib import Path


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
            """
            Validates the redaction process by comparing word counts before and after redaction.

            Parameters:
            - file (str): The path to the PDF file to be redacted.
            - num (int, optional): The number of redactions to generate. Default is 1.
            - input (list, optional): A list of input strings for selecting redactions. Default is an empty list.

            Returns:
            - None

            This function performs the following steps:
            1. Loads the original document, gets the word count before redaction (old).
            2. Performs redaction using the 'redact_file' function.
            3. Loads the redacted document, gets the word count after redaction (new).
            4. Checks if non-redacted words are still present in the original word count.
            5. Checks if all redactions have been removed from the original word count.

            """

            # File before redaction
            redactor1 = DocumentRedactor(file)
            old = redactor1.get_word_count()

            # Perform redaction
            redactions = redact_file(file, num, input, metadata=metadata)

            # File after redaction
            redactor2 = DocumentRedactor("temp.pdf")
            new = redactor2.get_word_count()

            if metadata:
                self.validate_metadata(redactor1, redactor2, redactions, [input[0]])

            # Check if non-redacted words are still present
            for new_word in new:
                if new_word in old:
                    with self.subTest(new_word=new_word):
                        # Check if subtraction of the word does not equal 0
                        self.assertNotEqual(old[new_word], 0, f"'{new_word}' occures more often than in the original file.")
                        old[new_word] -= new[new_word]
                else:
                    with self.subTest(new_word=new_word):
                        # Check if word that has not been found in the original file is a replacement value.
                        self.assertEqual(str(new_word).replace("[x]", ""), "", f"'{new_word}' was not in the original file. It seems it has been added while redacting the file.")

            # Check if all redactions have been removed from the file
            for i in redactions:
                for j in redactions[i]:
                    # Check if redaction is still left in the occurence count of the old file.
                    if j[4] in old:
                        with self.subTest(j=j):
                            # Check if subtraction of the redaction does not equal 0
                            self.assertNotEqual(old[j[4]], 0, f"Redaction '{j[4]}' occures more often than in the original file.")
                            old[j[4]] -= 1
                    else:
                        self.assertTrue(j[4] in old, f"'{j[4]}' can not be found as a redaction.")


    def validate_metadata(self, redactor_old: DocumentRedactor, redactor_new: DocumentRedactor, redactions, input):
        """
        Validates the metadata redaction process by comparing metadata before and after redaction.

        Parameters:
        - redactor_old (DocumentRedactor): The original DocumentRedactor instance.
        - redactor_new (DocumentRedactor): The DocumentRedactor instance after redaction.
        - redactions (dict): Dictionary of redactions per page.
        - input (list): List of input strings for selecting redactions.

        Returns:
        - None

        This method performs the following steps:
        1. Retrieves metadata before and after redaction.
        2. Compares metadata values for redacted words and input strings.
        3. Checks if redacted values in metadata match the expected redacted format "[x]".
        4. Compares XML metadata values for redacted words.
        5. Raises AssertionError if any of the validation checks fail.

        Note: The method uses the 'unittest' framework for test assertions.

        """

        # Step 1: Retrieve metadata before and after redaction.
        old_metadata = redactor_old.get_metadata()
        old_xml_metadata = ET.fromstring(redactor_old.doc.get_xml_metadata())
        new_metadata = redactor_new.get_metadata()
        new_xml_metadata = ET.fromstring(redactor_new.doc.get_xml_metadata())

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

    def test_simple(self):
        """
            Validate redaction for simple PDF documents.
        """
        for p in Path("./simple_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, input=["Lennaert"], metadata=True)

    def test_medium(self):
        """
            Validate redaction for moderate complex PDF documents.
        """
        for p in Path("./medium_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, input=["Lennaert"], metadata=True)

    def test_hard(self):
        """
            Validate redaction for difficult PDF documents.
        """
        for p in Path("./medium_pdf").glob('*.pdf'):
            with self.subTest(p=p):
                if p != "temp.pdf":
                    self.validate_redaction(p, input=["Lennaert"], metadata=True)

    # def test_1_simple_1(self):
    #     """
    #         Simple PDF with a few words and a header (1 redaction)
    #     """
    #     file = "./simple1.pdf"
    #     self.validate_redaction(file, num=1, input=["Lennaert"])

    # def test_1_simple_2(self):
    #     """
    #         Simple PDF with 4 lines and a header (5 redactions)
    #     """
    #     file = "./simple2.pdf"
    #     self.validate_redaction(file, num=5)

    # def test_1_simple_3(self):
    #     """
    #         Simple PDF with 4 big words (1 redaction)
    #     """
    #     file = "./simple3.pdf"
    #     self.validate_redaction(file, num=1)

    # def test_1_simple_4(self):
    #     """
    #         Simple PDF with one page full of words with a medium font size (5 redactions)
    #     """
    #     file = "./simple4.pdf"
    #     self.validate_redaction(file, num=5)

    # def test_1_simple_5(self):
    #     """
    #         Simple PDF with one page full of words with a medium font size (10 redactions)
    #     """
    #     file = "./simple4.pdf"
    #     self.validate_redaction(file, num=10)

    # def test_1_simple_6(self):
    #     """
    #         Simple PDF with one page full of words with a medium font size (25 redactions)
    #     """
    #     file = "./simple4.pdf"
    #     self.validate_redaction(file, num=25)

    # def test_2_medium_1(self):
    #     """
    #         Slightly complex PDF with half a page of text in a small fontsize. Text is made of
    #         multiple lines and two paragraphs (5 redactions)
    #     """
    #     file = "./medium1.pdf"
    #     self.validate_redaction(file, num=5)

    # def test_2_medium_2(self):
    #     """
    #         Slightly complex PDF with a page of text in a small fontsize. Text is made of
    #         multiple lines, paragraphs and two headers (10 redactions)
    #     """
    #     file = "./medium2.pdf"
    #     self.validate_redaction(file, num=10)

    # def test_2_medium_3(self):
    #     """
    #         Slightly complex PDF with two pages of text in a small fontsize. Text is made of
    #         multiple lines, paragraphs and headers (20 redactions)
    #     """
    #     file = "./medium3.pdf"
    #     self.validate_redaction(file, num=20)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()