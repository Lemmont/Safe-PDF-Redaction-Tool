import fitz
from DocumentRedactor import DocumentRedactor

def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/marx.pdf")
    pages = redactor.get_pages()
    for page in pages:
        redactor.prepare_page(page)
        dim = redactor.get_page_dimensions(page)
        (xref, lines, words) = redactor.get_page_contents(page)
        redactor.remove_positional_adjustments(lines, xref)

        # test redaction manually selected
        to_be_redacted = words[20]
        rect_of_to_be_redacted = fitz.Rect(to_be_redacted[0], to_be_redacted[1], to_be_redacted[2], to_be_redacted[3])

        redactor.add_redact_annot(page, rect_of_to_be_redacted)

        # Intermediate save with all to_be_redacted
        redactor.doc.save("res_temp.pdf")
        redactor.apply_redactions(page)

        (xref, lines, words) = redactor.get_page_contents(page)
        redactor.remove_positional_adjustments(lines, xref)

        to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, rect_of_to_be_redacted)
        redactor.reposition_words_same_line(to_be_repositioned, rect_of_to_be_redacted, lines, dim, xref)

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