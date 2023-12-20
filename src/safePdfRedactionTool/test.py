import os
import unittest
import sys
import fitz
from SafeRedaction import redact_file, DocumentRedactor


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

    def validate_redaction(self, file, num=1, input=[]):
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

            The function raises AssertionError if any of the validation checks fail.
            """

            # File before redaction
            redactor1 = DocumentRedactor(file)
            old = redactor1.get_word_count()

            # Perform redaction
            redactions = redact_file(file, num, input)

            # File after redaction
            redactor2 = DocumentRedactor("temp3.pdf")
            new = redactor2.get_word_count()

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

    def test_1_simple_1(self):
        """
            Simple PDF with a few words and a header (1 redaction)
        """
        file = "./simple1.pdf"
        self.validate_redaction(file, num=1)

    def test_1_simple_2(self):
        """
            Simple PDF with 4 lines and a header (5 redactions)
        """
        file = "./simple2.pdf"
        self.validate_redaction(file, num=5)

    def test_1_simple_3(self):
        """
            Simple PDF with 4 big words (1 redaction)
        """
        file = "./simple3.pdf"
        self.validate_redaction(file, num=1)

    def test_1_simple_4(self):
        """
            Simple PDF with one page full of words with a medium font size (5 redactions)
        """
        file = "./simple4.pdf"
        self.validate_redaction(file, num=5)

    def test_1_simple_5(self):
        """
            Simple PDF with one page full of words with a medium font size (10 redactions)
        """
        file = "./simple4.pdf"
        self.validate_redaction(file, num=10)

    def test_1_simple_6(self):
        """
            Simple PDF with one page full of words with a medium font size (25 redactions)
        """
        file = "./simple4.pdf"
        self.validate_redaction(file, num=25)

    def test_2_medium_1(self):
        """
            Slightly complex PDF with half a page of text in a small fontsize. Text is made of
            multiple lines and two paragraphs (5 redactions)
        """
        file = "./medium1.pdf"
        self.validate_redaction(file, num=5)

    def test_2_medium_2(self):
        """
            Slightly complex PDF with a page of text in a small fontsize. Text is made of
            multiple lines, paragraphs and two headers (10 redactions)
        """
        file = "./medium2.pdf"
        self.validate_redaction(file, num=10)

    def test_2_medium_3(self):
        """
            Slightly complex PDF with two pages of text in a small fontsize. Text is made of
            multiple lines, paragraphs and headers (20 redactions)
        """
        file = "./medium3.pdf"
        self.validate_redaction(file, num=20)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()