import os
import unittest
import sys
import fitz
from SafeRedaction import redact_file, DocumentRedactor


class ValidateCustomRedactions(unittest.TestCase):
    def setUp(self):
        os.chdir('/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/src/test_cases')

    def validate_redaction(self, file, num=1, input=[]):
            """
                Function to validate the redaction by comparing the input
                with the output using the redactions and the possible difference
                in occurences of words.
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