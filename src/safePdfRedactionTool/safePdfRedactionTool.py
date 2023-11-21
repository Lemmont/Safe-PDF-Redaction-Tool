from documentInterpreter import *
from documentReader import *
from documentManipulator import DocumentManipulator

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
    cmap = interpreter.parse_character_mapping(interpreter.fonts[6])
    content_stream = reader.get_content_from_stream(page_content[17])
    text_elements = interpreter.parse_text_elements(content_stream)
    text_translated = interpreter.translate_text_elements(text_elements, cmap )
    text_element_1 = list(text_elements.items())[0]

    content_streams = {6: content_stream}
    text_elements_6 = {6: text_elements}

    manipulator = DocumentManipulator(reader.doc, content_streams, text_elements_6)
    manipulator.remove_text(6, text_element_1)

    text_translated_after_removal = interpreter.translate_text_elements(manipulator.text_elements[6], cmap)
    print(text_translated)
    print(text_translated_after_removal)

    # remove text element 1

# Using the special variable
# __name__
if __name__=="__main__":
    main()