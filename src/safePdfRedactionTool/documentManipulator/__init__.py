import fitz

class DocumentManipulator:
    def __init__(self, document: fitz.Document):
        self.doc: fitz.Document = document

    def remove_text(self):
        """
            remove text
        """
        pass