import re
import fitz
from DocumentRedactor import DocumentRedactor

def select_multiple_redactions_example(words):
    return [words[19], words[21]]

def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/marx.pdf")
    pages = redactor.get_pages()
    for page in pages:
        redactor.prepare_page(page)
        dim = redactor.get_page_dimensions(page)
        (xref, lines, words) = redactor.get_page_contents(page)
        redactor.remove_positional_adjustments(lines, xref)

        # test redactions (on the same line) manually selected
        redactions = select_multiple_redactions_example(words)
        first_redaction = redactions[0]
        for redaction in redactions:
            rect = fitz.Rect(redaction[0], redaction[1], redaction[2], redaction[3])
            redactor.add_redact_annot(page, rect)

        # Intermediate save with all to_be_redacted
        redactor.doc.save("res_temp.pdf")
        redactor.apply_redactions(page)

        (xref, lines, words) = redactor.get_page_contents(page)

        # insert text "x" in first redaction
        test = fitz.Rect(first_redaction[0], first_redaction[1]-2, first_redaction[2], first_redaction[3]+5)
        test = redactor.insert_replacement_text(page, test)
        redactor.doc.save("res_temp2.pdf")

        (xref, lines, words) = redactor.get_page_contents(page)
        #print(lines)
        #print(lines)
        #redactor.remove_positional_adjustments(lines, xref)
        #print(lines)
        #(xref, lines, words) = redactor.get_page_contents(page)
        pattern = re.compile(r'<[^>]+>|\([^)]+\)')
        for i in range(len(lines)):
            if lines[i].endswith(b"TJ"):
                if b"Tm" not in lines[i] or b"Tf" not in lines[i]:
                    print(lines[i])
                    operands = lines[i].strip()[:-2].decode().strip()[1:-1]
                    res = re.sub(pattern, " ", operands).strip().split()
                    new = operands
                    if len(res) > 0:
                        for r in range(len(res)):
                            if r > 0:
                                new = new.replace(res[r], "-1")
                                operands = new
                            else:
                                #TODO calculate based on text
                                new = new.replace(res[r], "-500")
                                operands = new

                        lines[i] = b"[" + operands.encode() + b"]" + b" TJ"
                    print("ok", lines[i])


        to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, first_redaction, [test])
        redactor.reposition_words_same_line(to_be_repositioned, redactions, [test], lines, xref)

        redactor.finalize_redactions()
def main():
    """
    Example

    steps:
        for each page:
            read annotations/boxes/selected text
            retrieve text in boxes
            get cords/bounding box of text
            remove annots

            get lines of page
            get word of page

            add redact annots to page
            apply redactions

            get lines of page
            get word of page

            determine what to insert
            insert new text
            add white space before and after

            get lines of page
            get word of page

            remove white spaces
    """
    redact_example()

# Using the special variable
# __name__
if __name__=="__main__":
    main()