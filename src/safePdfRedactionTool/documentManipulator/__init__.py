import fitz
from typing import Dict, Tuple

class DocumentManipulator:
    """
        A class to manipulate PDF documents, i.e. remove text from a document.

        __init__
        :param document: the fitz document being worked on.
    """
    def __init__(self, document: fitz.Document, content_streams: Dict[int, str], text_elements: Dict[int, Dict[Tuple[float, float], any]]):
        self.doc: fitz.Document = document
        self.content_streams: Dict[int, str] = content_streams # {page_ref: content_stream}
        self.text_elements: Dict[int, Dict[Tuple[float, float], any]] = text_elements # {page_ref: {(x, y), text_info}}

    def remove_text(self, page, text_element) -> bool:
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

        # Get content stream of page
        content_stream = self.content_streams[page]

        for stream_item in content_stream:
            try:
                stream_item.replace(match, "")
                check = True
            except:
                continue

        if not check:
            return False

        # Update local stream
        self.content_streams[page] = content_stream

        # Update local text_elements
        self.text_elements[page].pop(cords)

        return True

    def update_cmap(self):
        pass

    def finalize_manipulation(self):
        """
            Update the document with the local edits; content_streams, metadata, font etc.
        """
        pass

    def save_document(self):
        pass
