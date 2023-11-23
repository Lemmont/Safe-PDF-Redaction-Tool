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

    def remove_white_space(self, page, content_obj, index, text_element) -> bool:
        """

        """
        cords = text_element[0]
        text_info = text_element[1]

        to_be_updated = []

        # get all cords on the same line after text_element
        prev_cord = cords[0]
        for item in self.text_elements[page][content_obj].items():
            if item[0][0] > cords[0] and item[0][1] == cords[1]:
                # get match and update it
                to_be_replaced = item[1]['match'].split("\n")[0].split(" ")[4]
                new_item = str(item[1]['match']).replace(str(to_be_replaced), str(float(to_be_replaced) - (float(to_be_replaced) - float(prev_cord))))
                to_be_updated.append((item[1]['match'], new_item))
                prev_cord = to_be_replaced # TODO: spacing fix

        print(to_be_updated)

        if page in self.edits_made and content_obj in self.edits_made[page] and index in self.edits_made[page][content_obj]:
            old_content = self.edits_made[page][content_obj][index]
            for item in old_content.items():
                old_content = item[1]
        else:
            old_content = self.text_streams[page][content_obj][index]

        temp = old_content
        for update in to_be_updated:
            new_string = str(temp).replace(update[0], update[1])
            temp = new_string



        # Update local stream
        #self.text_streams[page][index] = new_string

        # Update local text_elements
        #self.text_elements[page][content_obj].pop(cords)

        old_content = self.text_streams[page][content_obj][index]
        self.edits_made[page] = {content_obj: {index: {old_content: new_string}}}

        # Update edits_made

        return False

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
        if page in self.edits_made and content_obj in self.edits_made[page] and index in self.edits_made[page][content_obj]:
            old_content = self.edits_made[page][content_obj][index]
            for item in old_content.items():
                old_content = item[1]
        else:
            text_stream = self.text_streams[page][content_obj]
            old_content = text_stream[index]

        new_string = ""
        temp = old_content
        try:
            new_string = str(temp).replace(match, "")
            check = True
        except:
            check = False

        if not check:
            print("not found")
            return False

        # Update local stream
        #self.text_streams[page][index] = new_string

        # Update local text_elements
        self.text_elements[page][content_obj].pop(cords)

        # Update edits_made
        self.edits_made[page] = {content_obj: {index: {old_content: new_string}}}


        return True

    def update_cmap(self):
        pass

    def finalize_manipulation(self):
        """
            Update the document with the local edits; content_streams, metadata, font etc.
        """
        # Get all edits per page
        for key_edit in self.edits_made:
            # Get original content_stream for this edit
            for key_content_stream in self.edits_made[key_edit]:
                old_content = self.pages[key_edit][key_content_stream]['Stream']
                # Get all edits per content_stream object
                for key_index in self.edits_made[key_edit][key_content_stream]:
                    new_content = ""
                    # Get all edit per index
                    for key_item in self.edits_made[key_edit][key_content_stream][key_index]:
                        print(key_edit, key_content_stream, key_index, self.edits_made[key_edit][key_content_stream][key_index])
                        new_content = bytes(old_content.replace(key_item, self.edits_made[key_edit][key_content_stream][key_index][key_item]), "latin-1")
                        self.doc.update_stream(key_content_stream, new_content)
                        print("OKKK", new_content)

        print("Edits added!")


    def save_document(self):
        self.doc.save("../res.pdf")
        print("Succesfully saved!")
        pass
