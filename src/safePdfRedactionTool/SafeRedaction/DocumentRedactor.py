import logging
import fitz
import xml.etree.ElementTree as ET
from . import LineInterpreter as Li
from typing import Dict

logger = logging.getLogger(__name__)

class DocumentRedactor:
    def __init__(self, document):
        """
        Initializes an instance of YourClassName with the given document.

        Parameters:
        - document: The path to the PDF document.

        Raises:
        - ValueError: If the document is not a valid PDF file or if no file is given.
        """
        # Open the PDF document using PyMuPDF (fitz) and assign it to self.doc
        self.doc: fitz.Document = fitz.open(document, filetype="pdf")

        # Check if the file given is valid. Otherwise, raise a ValueError.
        if self.doc.page_count == 0:
            raise ValueError("No file given or not a valid file.")

        # Obtain a list of page objects for the given document
        self.pages = [page for page in self.doc.pages()]

        # Dictionary to store redactions per page (to be added or already added)
        self.redactions: Dict = None

        # Dictionary to store possible replacement texts per page
        self.replacements_per_page = {}

        # Dictionary to store words of this document
        self.words_dict: Dict = None

        # Dictionary to map redactions to textblocks on each page
        self.redacts_textblocks_per_page = {}



    def __str__(self) -> str:
        """
        String representation of a Redactor object. Gives information about the file.

        Returns:
        - str: A string containing information about the Redactor object and the associated document.
        """
        msg = "--- REDACTOR ---\n"

        # Check if a document is associated with the Redactor object
        if self.doc:
            msg += "\n-- File Information --\n"
            msg += " name        " + self.doc.name + "\n"  # Append document name
            msg += " pages       " + str(self.doc.page_count) + "\n"  # Append page count
            msg += " emb. files  " + str(self.doc.embfile_count()) + "\n"  # Append embedded file count
        else:
            msg += "No (valid) file inserted\n"  # If no document is associated

        return msg  # Return the string representation of the Redactor object

    def get_word_count(self):
        """
        Get the occurrence of every word in the document.

        Returns:
        - dict: A dictionary where keys are unique words in the document,
                and values are the occurrences of each word.
        """
        # Initialize an empty dictionary to store word occurrences
        words = {}

        # Iterate through each page in the document
        for page in self.doc.pages():
            # Get a list of words on the page, sorted by position
            page_words = page.get_text("words", sort=True)

            # Iterate through each word on the page
            for i in page_words:
                # Check if the word is already in the dictionary
                if i[4] in words:
                    # If yes, increment the count
                    words[i[4]] += 1
                else:
                    # If no, add the word to the dictionary with count 1
                    words[i[4]] = 1

        # Return the dictionary containing word occurrences
        return words

    def get_metadata(self):
        """
        Get the metadata of the PDF document.

        Returns:
        - str: Metadata of the PDF document.
        """
        # Return the metadata of the PDF document
        return self.doc.metadata


    def add_redactions(self, redactions=None):
        """
        Add redactions to the PDF document.

        Parameters:
        - redactions (dict): A dictionary containing redaction information per page.
                            Format: {page_number: [[x0, y0, x1, y1], ...], ...}
                            If None or an empty dictionary, no redactions are added.

        Returns:
        - None
        """
        # Check if redactions are provided and are not empty
        if redactions is None or redactions == {}:
            print("No redactions")
            return

        # Set the provided redactions to the instance attribute
        self.redactions = redactions

        # Iterate through each page in the document
        for page in self.pages:

            # Check if there are redactions for the current page
            if page in self.redactions:
                page_redactions = self.redactions[page]

                # Get page contents
                xref, lines, words, text_blocks = _get_page_contents(page)

                # Get mapping of redactions to text blocks on the page
                redacts_to_textblocks = _get_redactions_to_textblock(page_redactions, text_blocks)
                self.redacts_textblocks_per_page[page] = redacts_to_textblocks

                # Iterate through each redaction on the page
                for redaction in page_redactions:
                    rect = fitz.Rect(redaction[0], redaction[1], redaction[2], redaction[3])

                    # Adjust the redact annotation to make it small
                    h = rect.height
                    my = (rect.y0 + rect.y1) / 2
                    y0 = my - h * 0.1
                    y1 = my + h * 0.1
                    rect.y0 = y0
                    rect.y1 = y1

                    # Add the redaction to the page
                    self.add_redaction(page, rect)


    def apply_redactions_without_replacements(self):
        """
        Apply redactions without replacements to the PDF document.

        Returns:
        - None
        """
        # Check if redactions are provided and are not empty
        if self.redactions is None or self.redactions == {}:
            print("No redactions to be removed")
            return

        # Iterate through each page in the document
        for page in self.pages:
            # Apply redactions for the current page
            _apply_redactions(page)

            # Initialize an empty list for replacements on the current page
            self.replacements_per_page[page] = []


    def apply_redactions_with_replacements(self):
        """
        Apply redactions with replacements to the PDF document.

        Returns:
        - None
        """
        # Check if redactions are provided and are not empty
        if self.redactions is None or self.redactions == {}:
            print("No redactions")
            return

        # Iterate through each page in the document
        for page in self.pages:
            # Check if there are redactions for the current page
            if page in self.redactions:
                page_redactions = self.redactions[page]

                # Get the words dictionary for the current page
                self.words_dict = page.get_text("dict")
                xref, lines, words, text_blocks = _get_page_contents(page)

                # Apply redactions for the current page
                _apply_redactions(page)

                # Add replacements for the redactions on the current page
                replacements_texts_rects = _add_replacements(page_redactions, page, self.words_dict, xref)
                self.replacements_per_page[page] = replacements_texts_rects



    def edit_positional_information(self):
        """
        Edit the positional information of redactions and replacements on each page.

        Returns:
        - None
        """
        # Check if redactions are provided and are not empty
        if self.redactions is None or self.redactions == {}:
            print("No redactions")
            return

        # Iterate through each page in the document
        for page in self.pages:
            # Get redactions, replacements, and redacts to textblocks mapping for the current page
            page_redactions = self.redactions[page]
            page_replacements = self.replacements_per_page[page]
            page_redacts_to_textblocks = self.redacts_textblocks_per_page[page]

            # Get dimensions of the page
            dim = _get_page_dimensions(page)

            # Clean the page (potentially remove existing redactions)
            _clean_page(page)

            # Get page contents
            xref, lines, words, text_blocks = _get_page_contents(page)

            # Get redactions and replacements per line on the page
            redaction_per_line, replacements_per_line = _get_redactions_per_line(page_redactions, page_replacements)

            # Get lines and commands per line on the page
            lines_per_line = _get_command_lines_per_line(page_redactions, lines, page_redacts_to_textblocks, dim)

            # Initialize a LineManipulator to update positions
            manipulator = Li.LineManipulator(lines_per_line, redaction_per_line, replacements_per_line, lines)

            # Update positions and get the modified lines
            new = manipulator.update_positions_lines()

            # Update the page stream with the modified lines
            self.doc.update_stream(xref, b"\n".join(new))

            # Refresh page contents after updating positions
            xref, lines, words, text_blocks = _get_page_contents(page)

            # Iterate through redactions per line for further adjustments
            for i in redaction_per_line:
                redactions_on_line = redaction_per_line[i]
                replacements_on_line = replacements_per_line[i]

                # Get words to be repositioned on the same line
                to_be_repositioned = _get_to_be_repositioned_words(dim[1], lines, redactions_on_line[0], replacements_on_line)

                # Reposition words on the same line
                _reposition_words_same_line(self.doc, to_be_repositioned, redactions_on_line, replacements_on_line, lines, xref)

        # Refresh the list of pages after editing positional information
        self.pages = [page for page in self.doc.pages()]

    def add_redaction(self, page: fitz.Page, rect: fitz.Rect):
        """
        Add redaction to the defined rectangle on the specified page.

        Parameters:
        - page (fitz.Page): The page to which the redaction will be added.
        - rect (fitz.Rect): The rectangle defining the area to be redacted.

        Returns:
        - None
        """
        # Add a redaction annotation to the specified rectangle on the page
        page.add_redact_annot(rect.quad)

    def finalize_redactions(self, redactions, new_filename="redacted.pdf"):
        """
        Save the redacted PDF document and return the redactions.

        Parameters:
        - redactions: The redactions made in the PDF document.
        - new_filename (str): The filename for the redacted PDF. Default is "redacted.pdf".

        Returns:
        - redactions: The redactions made in the PDF document.
        """
        # Save the redacted PDF document with the specified filename
        self.doc.save(new_filename)

        # Return the redactions
        return redactions

    def redact_xml_metadata(self, redactions, inputs=[]):
        """
            Redact values from XML metadata based on previous redactions and inputs
        """

        xml_metadata = self.doc.get_xml_metadata()
        if xml_metadata == "":
           #print("No xml metadata")
            return

        to_be_redacted = set()

        # Possibly add one or more redacted values
        for i in redactions:
            for j in redactions[i]:
                word = j[4]
                to_be_redacted.add(word)

        # Possibly add one or more inputs
        for i in inputs:
            to_be_redacted.add(i)

        root = ET.fromstring(xml_metadata)

        for item in to_be_redacted:
            for elem in root.iter():
                value = elem.text
                if value != None and item in value:
                    elem.text = ""

        modified_xml_data = ET.tostring(root, encoding='unicode')
        self.doc.set_xml_metadata(modified_xml_data)

    def redact_metadata(self, redactions, inputs=[]):
        """
            Check metadata for possible values/text/entries to be redacted based
            on the possible inputs and redactions that have been in the document.
        """
        metadata = self.doc.metadata
        if metadata == "" or metadata == {}:
            #print("No metadata")
            return

        to_be_redacted = set()

        # Possibly add one or more redacted values
        for i in redactions:
            for j in redactions[i]:
                word = j[4]
                to_be_redacted.add(word)

        # Possibly add one or more inputs
        for i in inputs:
            to_be_redacted.add(i)

        # Loop over redaction values
        for item in to_be_redacted:
            for q in metadata:
                if metadata[q] != None and item in metadata[q]:
                    metadata[q] = str(metadata[q]).replace(item, "")

    def redact_toc(self, redactions, input=[]):
        """
            Check table of contents for possible values/text/entries to be redacted based
            on the possible inputs and redactions that have been in the document.
        """
        toc = self.doc.get_toc()
        if toc == "" or toc == [] or toc == None:
            #print("No table of contents")
            return

        to_be_redacted = set()

        # Possibly add one or more redacted values
        for i in redactions:
            for j in redactions[i]:
                word = j[4]
                to_be_redacted.add(word)

        # Possibly add one or more inputs
        for i in input:
            to_be_redacted.add(i)

        for item in to_be_redacted:
            for e in range(len(toc)):
                text = str(toc[e][1])
                page = toc[e][2]
                if item in text:
                    self.doc.set_toc_item(e, title=text.replace(item, ""))

def _apply_redactions(page: fitz.Page):
        """
        Apply all redactions to the specified page.

        Parameters:
        - page (fitz.Page): The page to which redactions will be applied.

        Returns:
        - None
        """
        # Apply all redactions to the specified page
        page._apply_redactions()

def _get_page_dimensions(page: fitz.Page):
        """
        Get the crop box dimensions of the specified page.

        Parameters:
        - page (fitz.Page): The page for which to retrieve dimensions.

        Returns:
        - tuple: A tuple containing the x1 and y1 coordinates of the crop box.
        """
        # Get the crop box dimensions of the specified page
        cropbox = page.cropbox
        return (cropbox.x1, cropbox.y1)

def _get_redactions_to_textblock(redactions, text_blocks):
        """
        Determine in which text block a redaction is situated.

        Parameters:
        - redactions (list): List of redaction rectangles, each represented as [x0, y0, x1, y1].
        - text_blocks (list): List of text blocks, each represented as a Fitz rectangle.

        Returns:
        - dict: A dictionary mapping each redaction rectangle (fitz.Rect) to its corresponding text block (fitz.Rect).
        """
        redacts_to_textblocks = {}

        # Iterate through each redaction rectangle
        for redaction_coords in redactions:
            redact_rect = fitz.Rect(redaction_coords[0], redaction_coords[1], redaction_coords[2], redaction_coords[3])

            # Check which text block contains the redaction rectangle
            for text_block_rect in text_blocks:
                if text_block_rect.contains(redact_rect):
                    redacts_to_textblocks[redact_rect] = text_block_rect

        return redacts_to_textblocks

def _clean_page(page: fitz.Page):
        page.clean_contents()

def _get_page_contents(page):
        """
            returns xref, lines and words of page.
        """
        xref = page.get_contents()[0]
        lines = page.read_contents().splitlines()
        words = page.get_text("words", sort=True)

        text_blocks = []
        blocks = page.get_text("blocks", sort=True)
        for i in range(len(blocks)):
            # [0:4]: b-boxes of text blocks.
            rect = fitz.Rect(blocks[i][0], blocks[i][1], blocks[i][2], blocks[i][3])
            text_blocks.append(rect)

        return (xref, lines, words, text_blocks)

def _insert_replacement_text(page: fitz.Page, rect: fitz.Rect, fontsize):
    """
        Insert replacement text in rect. of redacted text

    """
    space = -1

    # Font used for inserted text. TODO: needs to be added to document
    font_used = "courier"
    font = fitz.Font(font_used)


    # New length of text
    new_length = font.text_length("[x]",fontsize=fontsize)

    # New height needed for text based on fontsize
    new_height = (font.ascender - font.descender) * fontsize

    # New x1
    newx1 = rect[0] + new_length

    # New rect for text to be inserted
    new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[1] + new_height)
    while space < 0:
        space = page.insert_textbox(new_rect, "[x]", fontname=font_used, fontsize=fontsize)
        new_height -= space
        new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[1] + new_height)
    return new_rect

def _get_to_be_repositioned_words(page_height, lines, first_redaction: fitz.Rect, replacements):
    to_be_repositioned = []
    for i in range(len(lines)):

        #print(lines[i])
        if lines[i].endswith(b"Tm"):
            temp = False
            string_line = lines[i].split()
            x = float(string_line[4])
            y = page_height - float(string_line[5])
            #print(lines[i], x, y)
            for replacement in replacements:
                #print(replacement, x, y)
                if x > round(replacement[0],3) and y >= replacement[1] and y <= replacement[3]:
                    continue
            if x > first_redaction[0] and  y >= first_redaction[1] and y <= first_redaction[3]:
                for j in range(i, len(lines)):
                    if lines[j].endswith(b"TJ") or lines[j].endswith(b"Tj"):
                        to_be_repositioned.append((lines[i], i, j))

    # filter out the replacement texts
    return to_be_repositioned

def _reposition_words_same_line(doc, to_be_repositioned, redactions, replacements, lines, xref):
    """
        Reposition the to be repositioned words based on the first redaction
        on the line.
    """
    #print(redactions, replacements)
    diff = 0
    length = 0
    for i in range(len(to_be_repositioned)):
        string_line = to_be_repositioned[i][0].split()
        x = float(string_line[4]) if len(string_line) > 4 else float(string_line[0])
        for j in range(len(redactions)):
            if x >= redactions[j][2]:
                if replacements != []:
                    diff += (redactions[j][2]-redactions[j][0]) - replacements[j].width
                else:
                    diff += (redactions[j][2]-redactions[j][0])
            else:
                break
        #print(i, diff)
        if (i > 0) or (len(redactions) > 1 and len(to_be_repositioned) == 1):
            new_pos = x - diff
        else:
            new_pos = redactions[0][0]

        if len(string_line) > 3:
            string_line[4] = str(new_pos).encode()
        else:
            string_line[0] = str(new_pos).encode()

        new_string = b" ".join(string_line)
        #print(x, new_string, diff)

        lines[to_be_repositioned[i][1]] = new_string

        diff = 0
    if len(to_be_repositioned) > 0:
        doc.update_stream(xref, b"\n".join(lines))

def _get_redaction_info(redaction, words_dict):
    """
        Get information about the redacted text, i.e. fontsize.
    """
    block = redaction[5]
    line = redaction[6]

    block = block if (block == len(words_dict['blocks']) - 1) else block + 1
    res = words_dict["blocks"][block]

    if 'lines' in res:
        if line in res:
            res = words_dict["blocks"][block]["lines"][line]
        else:
            res = words_dict["blocks"][block]["lines"][0]
    else:
        return 7.0

    if 'spans' in res:
        res = res['spans']
        #print("SPANS FOUND","\n",span, res)
        if len(res) == 1:
            res = res[0]
            #print(res)
        else:
            #print("MORE","\n", len(res), res)
            for i in range(0, len(res)):
                if redaction[4] in res[i]['text']:
                    res = res[i]
                    break
    else:
        #print("NO SPANS","\n", res)
        return 7.0

    try:
        fontsize = res['size']
    except TypeError:
        fontsize = res[0]['size']

    return fontsize

def _add_replacements( redactions, page, words_dict, xref):
    replacements_texts_rects = []
    for i in range(len(redactions)):
        fontsize = _get_redaction_info(redactions[i], words_dict)
        rect = fitz.Rect(redactions[i][0], redactions[i][1] , redactions[i][2], redactions[i][3] )
        new_rect = _insert_replacement_text(page, rect, fontsize)
        replacements_texts_rects.append(new_rect)
    return replacements_texts_rects

def _get_redactions_per_line(redactions, replacements):
    """
        Determine which redactions and replacements are on the same line
        (between same y_0 and y_1)
    """
    redaction_per_line = {}
    replacements_per_line = {}
    lines_per_line = {}
    # Determine all redactions on a line, based on the y-cords.
    for i in range(len(redactions)):

        # Get y-cords for the line on which the redaction is on
        y_cords = (redactions[i][1], redactions[i][3])

        # If a redaction with y_cords is already present, add to redactions per line for y_cords
        if y_cords in redaction_per_line:
            redaction_per_line[y_cords].append(redactions[i])
            if replacements != []:
                replacements_per_line[y_cords].append(replacements[i])

        # If not, add new key-value pair.
        elif y_cords in lines_per_line:
            continue
        else:
            redaction_per_line[y_cords] = [redactions[i]]
            if replacements != []:
                replacements_per_line[y_cords] = [replacements[i]]
            else:
                replacements_per_line[y_cords] = []

    return (redaction_per_line, replacements_per_line)

def _get_command_lines_per_line(redactions, lines, redacts_to_textblocks, dim):
    lines_per_line = {}
    for i in range(len(redactions)):
        # Get y-cords for the line on which the redaction is on
        y_cords = (redactions[i][1], redactions[i][3])
        if y_cords not in lines_per_line:
            lines_per_line[y_cords] = [(redactions[i][0], redactions[i][2])]
            for j in range(len(lines)):
                if lines[j].endswith(b"Tm"):
                    x = float(lines[j].split()[4].decode())
                    y = dim[1] - float(lines[j].split()[5].decode())
                    rect = fitz.Rect(redactions[i][0], redactions[i][1], redactions[i][2], redactions[i][3])
                    block_cords = redacts_to_textblocks[rect]
                    if y >= round(redactions[i][1], 3) and y <= round(redactions[i][3]) and y >= round(block_cords[1], 3) and y <= round(block_cords[3], 3) and x >= round(block_cords[0], 3) and x <= round(block_cords[2], 3):
                        for q in range(j + 1, len(lines)):
                            if lines[q].endswith(b"TJ"):
                                lines_per_line[y_cords].append((lines[q], q, j))
                                break
                            elif lines[q].endswith(b"Tj"):
                                break
    return lines_per_line