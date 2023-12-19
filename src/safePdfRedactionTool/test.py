import os
import unittest
import sys
import fitz
from SafeRedaction import redact_file, DocumentRedactor


class ValidateCustomRedactions(unittest.TestCase):
    def setUp(self):
        os.chdir('/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/src/test_cases')
        self.docs = {
            "test_simple_1" : 'simple1.pdf',
            "test_simple_2" : 'simple2.pdf',
            "test_simple_3" : 'simple3.pdf',
            "test_simple_4" : 'simple4.pdf',
            }

    def test_simple_1(self):
        """
            Simple PDF with a few words and a header (1 redaction)
        """
        file = self.docs['test_simple_1']
        redactor1 = DocumentRedactor(file)
        old = redactor1.get_word_count()
        redact_file(file, num=1)
        redactor2 = DocumentRedactor("temp3.pdf")
        new = redactor2.get_word_count()
        print(old)
        print(new)

        for new_word in new:
            if new_word[4] in old:
                old[new_word[4]] -= 1
            else:
                if new_word[4] != "[x]":
                    print("error", new_word)
                    return False


        # compare old and new

        # m1 = redactor1.get_metadata()
        # for q in m1:
        #     print(q, m1[q])

        # for page in new.pages():
        # wordsNew = page.get_text("words", sort=True)
        # for i in wordsNew:
        #     if i[4] in wOld:
        #         wOld[i[4]] -= 1
        #     else:
        #         if i[4] != "[x]":
        #             print("error", i)
        #             return False

        # # Check all left over words from the old file and if they are a redaction
        # for i in redactions:
        #     for j in redactions[i]:
        #         if j[4] in wOld:
        #             if wOld[j[4]] == 0:
        #                 return False
        #             else:
        #                 wOld[j[4]] -= 1
        #         else:
        #             return False


    # def test_simple_2(self):
    #     """
    #         Simple PDF with more words and a header (5 redactions)
    #     """
    #     file = self.docs['test_simple_2']
    #     old = file
    #     redactions = redact_file(file, inputs=[], num=5)
    #     new = file.split(".")[0] + "-res.pdf"
    #     self.assertTrue(compare_content(old, new, redactions))

    # def test_simple_3(self):
    #     """
    #         Simple PDF with few words with a bigger fontsize (1 redaction)
    #     """
    #     file = self.docs['test_simple_3']
    #     old = file
    #     redactions = redact_file(file, inputs=[], num=1)
    #     new = file.split(".")[0] + "-res.pdf"
    #     self.assertTrue(compare_content(old, new, redactions))

    # def test_simple_4(self):
    #     """
    #         Simple PDF with one full page with bigger fontsize (20 redactions)
    #     """
    #     file = self.docs['test_simple_4']
    #     old = file
    #     redactions = redact_file(file, inputs=[], num=20)
    #     new = file.split(".")[0] + "-res.pdf"
    #     self.assertTrue(compare_content(old, new, redactions))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()