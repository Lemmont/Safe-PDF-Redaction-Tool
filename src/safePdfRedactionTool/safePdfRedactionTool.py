import fitz
from DocumentRedactor import DocumentRedactor

def select_multiple_redactions_example(words):
    return [words[0]]

def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/pdf2Roboto.pdf")
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

        # insert text "x" in first redaction
        test = fitz.Rect(first_redaction[0], first_redaction[1]-2, first_redaction[2], first_redaction[3]+5)
        redactor.insert_replacement_text(page, test)
        redactor.doc.save("res_temp2.pdf")

        (xref, lines, words) = redactor.get_page_contents(page)
        redactor.remove_positional_adjustments(lines, xref)

        to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, first_redaction, test)
        redactor.reposition_words_same_line(to_be_repositioned, redactions, test, lines, xref)

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