import fitz
from typing import Dict, Tuple

class DocumentManipulator:
    """
        A class to manipulate PDF documents, i.e. remove text from a document.

        __init__
        :param document: the fitz document being worked on.
    """
    def __init__(self, document: fitz.Document, text_streams: Dict[int, Dict[int, any]], pages, text_elements: Dict[int, Dict[Tuple[float, float], any]]):
        self.doc: fitz.Document = document
        self.text_streams: Dict[int, Dict[int, any]] = text_streams # {page_ref: content_stream}
        self.pages = pages
        self.text_elements: Dict[int, Dict[Tuple[float, float], any]] = text_elements # {page_ref: {(x, y), text_info}}
        self.edits_made = {}

    def remove_text(self, page, content_obj, index, text_element) -> bool:
        """
            Remove 'text_element' from document

            :param page: reference to the page where text should be removed.
            :param text_element: text element to be removed from the document

            :result: true or false based on the fact
        """
        check = False

        # TODO: multiple text elements to account for words being split up in
        # multiple text elements.

        # Get coordinates of text
        cords = text_element[0]

        # Get text information
        text_info = text_element[1]

        # Get reference to content stream string
        match = text_info['match']

        # Get text stream of page
        text_stream = self.text_streams[page][content_obj]
        old_content = text_stream[index]

        new_string = ""
        try:
            new_string = str(text_stream[index]).replace(match, " ")
            print(len(new_string))
            check = True
        except:
            check = False

        if not check:
            print("not found")
            return False

        # Update local stream
        self.text_streams[page][index] = new_string

        # Update local text_elements
        self.text_elements[page][content_obj].pop(cords)

        # Update edits_made
        print("OK", len(old_content), len(new_string), check)
        self.edits_made[page] = {content_obj: {index: {old_content: new_string}}}

        return True

    def update_cmap(self):
        pass

    def finalize_manipulation(self):
        """
            Update the document with the local edits; content_streams, metadata, font etc.
        """
        print(self.edits_made)
        for page_edits in self.edits_made.items():
            for content_stream in page_edits[1].items():
                old_content = str(self.pages[page_edits[0]][content_stream[0]]['Stream'])
                for index in content_stream[1].items():
                    new_content = ""
                    for item in index[1].items():
                        print("Ok", item)
                        new_content = bytes(old_content.replace(item[0], item[1]), "latin-1")
                        self.doc.update_stream(content_stream[0], new_content)

    def save_document(self):
        self.doc.save("../res.pdf")
        pass
