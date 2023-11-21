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

    fonts = {}
    contents = {}

    for page_xref in pagesDoc:
        fonts[page_xref] = reader.get_page_fonts(pagesDoc[page_xref])
        page_content = reader.get_page_content(pagesDoc[page_xref])
        temp_content = {}
        for cnt in page_content.items():
            temp_content[cnt[0]] = cnt[1]
        contents[page_xref] = temp_content

    #print(fonts)
    #print(contents)

    interpreter = DocumentInterpreter(reader.doc, pagesDoc, fonts, contents)

    cmaps = {}
    text_contents = {}
    text_elements = {}

    for page_xref in pagesDoc:
        cmap = interpreter.parse_character_mapping(interpreter.fonts[page_xref])
        temp_text_elements = {}
        temp_text_contents = {}
        for content_xref in contents[page_xref]:
            text_content = reader.get_content_from_stream(contents[page_xref][content_xref])
            temp_text_elements[content_xref] = interpreter.parse_text_elements(text_content)
            temp_text_contents[content_xref] = text_content

        cmaps[page_xref] = cmap
        text_contents[page_xref] = temp_text_contents
        text_elements[page_xref] = temp_text_elements

    #print(cmaps)
    #print(text_contents)
    #print(text_elements)


    manipulator = DocumentManipulator(reader.doc, text_contents, contents, text_elements)
    test_text_element = text_elements[6][17][(226.935, 721.212)]
    manipulator.remove_text(6, 17, 0, ((226.935, 721.212), test_text_element))
    manipulator.finalize_manipulation()
    manipulator.save_document()

    """
    # page 6
    page_content = reader.get_page_content(pagesDoc[6])
    page_fonts = {6: reader.get_page_fonts(pagesDoc[6])}

    interpreter = DocumentInterpreter(reader.doc, pagesDoc, fonts)
    cmap = interpreter.parse_character_mapping(interpreter.fonts[6])
    text_content = reader.get_content_from_stream(page_content[17]) # content_stream = BT...ET
    text_elements = interpreter.parse_text_elements(text_content)
    text_translated = interpreter.translate_text_elements(text_elements, cmap )
    text_element_1 = list(text_elements.items())[0]

    text_streams = {6: text_content}
    text_elements_6 = {6: text_elements}

    manipulator = DocumentManipulator(reader.doc, text_streams, {6: page_content[17]}, text_elements_6)
    manipulator.remove_text(6, 0, text_element_1)

    text_translated_after_removal = interpreter.translate_text_elements(manipulator.text_elements[6], cmap)
    print(text_translated)
    print(text_translated_after_removal)
    manipulator.finalize_manipulation()
    manipulator.save_document()
    """


    # remove text element 1

# Using the special variable
# __name__
if __name__=="__main__":
    main()