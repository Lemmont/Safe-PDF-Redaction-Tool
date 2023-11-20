from documentInterpreter import *
from documentReader import *

def main():
    """
    Example
    """
    reader = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/marx.pdf")
    root = reader.get_root_object()
    pagesObj = reader.get_pages_object(root['Pages'])
    pagesDoc = reader.get_pages(pagesObj['Kids'])
    # page 6
    page_content = reader.get_page_content(pagesDoc[6])
    page_fonts = {6: reader.get_page_fonts(pagesDoc[6])}

    interpreter = DocumentInterpreter(reader.doc, pagesDoc, page_fonts)
    #print(interpreter.parse_character_mappings(interpreter.fonts[6]))

# Using the special variable
# __name__
if __name__=="__main__":
    main()