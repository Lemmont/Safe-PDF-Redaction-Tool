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

        # Original text streams of the document
        self.text_streams: Dict[int, Dict[int, any]] = text_streams # {page_ref: content_stream}
        self.pages = pages

        # Text elements of the document. Gets updated.
        self.text_elements: Dict[int, Dict[Tuple[float, float], any]] = text_elements # {page_ref: {(x, y), text_info}}
        self.edits_made = {}

    def remove_white_space(self, page, content_obj, index, text_element) -> bool:
        """
            Remove white spaces after deletion of a given text element.

            Shifts all text elements right of a given text element to the left based

            :param page: integer reference number
            :param content_obj: integer reference to content object of page
            :param index: integer internal representation of text elements
            :param text_element: text_element internal representation whereafter
                text elements should be shifted and white spaces should be removed.
        """
        # Get cords of the text element that got deleted
        cords = text_element[0]

        # List of to be updated text_elements
        to_be_updated = []

        length = 0.0
        line_cords = []
        # Get all cords on the same line after text_element
        for key in self.text_elements[page][content_obj]:
            if key[0] > cords[0] and key[1] == cords[1]:
                line_cords.append(key)

        #TODO: check if there are text elements after the given text_element

        # Determine x position of every text element after the given text_element.
        for i in range(len(line_cords)):
            # Get text element
            item = self.text_elements[page][content_obj][line_cords[i]]
            to_be_replaced = item['match'].split("\n")[0].split(" ")[4]

            # Calculate new x position of the text element
            if i == 0:
                new_pos = float(cords[0])
            else:
                length += (float(line_cords[i - 1][0]) - float(line_cords[i][0]))
                new_pos = cords[0] - length

            # Replace old x position with new x position.
            new_item = str(item['match']).replace(str(to_be_replaced), str(new_pos))
            to_be_updated.append((item['match'], new_item))

        # Check if there is already an edit for this page, object and index.
        if page in self.edits_made and content_obj in self.edits_made[page] and index in self.edits_made[page][content_obj]:
            old_content = self.edits_made[page][content_obj][index]
            for item in old_content.items():
                old_content = item[1]
        else:
            old_content = self.text_streams[page][content_obj][index]

        # Apply updates in the stream of the old_content.
        temp = old_content
        for update in to_be_updated:
            new_string = str(temp).replace(update[0], update[1])
            temp = new_string


        # TODO: Update local text_elements
        #self.text_elements[page][content_obj].pop(cords)

        # Update edits_made.
        old_content = self.text_streams[page][content_obj][index]
        self.edits_made[page] = {content_obj: {index: {old_content: new_string}}}

        print(f"Removed white spaces and shifted text to the left after {cords} on page {page}, content stream {content_obj} and index {index}")

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
            for key in old_content:
                old_content = old_content[key]
        else:
            text_stream = self.text_streams[page][content_obj]
            old_content = text_stream[index]

        new_string = ""
        temp = old_content

        # Update/remove if it exists.
        try:
            new_string = str(temp).replace(match, "")
            check = True
        except:
            check = False

        if not check:
            print("not found")
            return False


        # Update local text_elements by removing from text_elements
        self.text_elements[page][content_obj].pop(cords)

        old_content = self.text_streams[page][content_obj][index]

        # Update edits_made
        self.edits_made[page] = {content_obj: {index: {old_content: new_string}}}

        print(f"Removed text at {cords} on page {page}, content stream {content_obj} and index {index}")

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
                        #print(key_edit, key_content_stream, key_index, self.edits_made[key_edit][key_content_stream][key_index])
                        new_content = bytes(old_content.replace(key_item, self.edits_made[key_edit][key_content_stream][key_index][key_item]), "latin-1")
                        self.doc.update_stream(key_content_stream, new_content)
                        #print("OKKK", new_content)

        print("Edits added!")


    def save_document(self):
        self.doc.save("../res.pdf")
        print("Succesfully saved!")
        pass
