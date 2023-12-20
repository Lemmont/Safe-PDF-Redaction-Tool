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
        """
        Clean the contents of the specified page.

        Parameters:
        - page (fitz.Page): The page to be cleaned.

        Returns:
        - None
        """
        # Clean the contents of the specified page
        page.clean_contents()

def _get_page_contents(page):
    """
    Return xref, lines, words, and text blocks of the specified page.

    Parameters:
    - page: The page for which to retrieve contents.

    Returns:
    - tuple: A tuple containing xref, lines, words, and text blocks of the page.
    """
    # Get the xref of the page
    xref = page.get_contents()[0]

    # Read the contents of the page and split into lines
    lines = page.read_contents().splitlines()

    # Get the words on the page, sorted
    words = page.get_text("words", sort=True)

    # Get the text blocks on the page
    text_blocks = []
    blocks = page.get_text("blocks", sort=True)
    for i in range(len(blocks)):
        # Create a Rect object representing the bounding box of the text block
        rect = fitz.Rect(blocks[i][0], blocks[i][1], blocks[i][2], blocks[i][3])
        text_blocks.append(rect)

    return xref, lines, words, text_blocks

def _insert_replacement_text(page: fitz.Page, rect: fitz.Rect, fontsize):
    """
    Insert replacement text in the rectangle of redacted text.

    Parameters:
    - page (fitz.Page): The page on which to insert replacement text.
    - rect (fitz.Rect): The rectangle of the redacted text where replacement text will be inserted.
    - fontsize: The font size of the replacement text.

    Returns:
    - fitz.Rect: The new rectangle representing the area occupied by the inserted replacement text.
    """
    space = -1

    # Font used for inserted text. TODO: needs to be added to document
    font_used = "courier"
    font = fitz.Font(font_used)

    # Calculate the length of the replacement text
    new_length = font.text_length("[x]", fontsize=fontsize)

    # Calculate the height needed for the text based on the font size
    new_height = (font.ascender - font.descender) * fontsize

    # Calculate the new x1 coordinate
    newx1 = rect[0] + new_length

    # Create a new rectangle for the text to be inserted
    new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[1] + new_height)

    # Attempt to insert the text into the rectangle, adjusting the height if needed
    while space < 0:
        space = page.insert_textbox(new_rect, "[x]", fontname=font_used, fontsize=fontsize)
        new_height -= space
        new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[1] + new_height)

    return new_rect

def _get_to_be_repositioned_words(page_height, lines, first_redaction: fitz.Rect, replacements):
    """
    Identify words in the PDF page that need to be repositioned.

    Parameters:
    - page_height: The height of the PDF page.
    - lines: List of lines in the PDF content.
    - first_redaction (fitz.Rect): The rectangle of the first redaction.
    - replacements: List of replacement rectangles.

    Returns:
    - list: List of lines that need to be repositioned.
    """
    to_be_repositioned = []

    # Iterate through each line in the PDF content
    for i in range(len(lines)):

        # Check if the line ends with "Tm" (text matrix)
        if lines[i].endswith(b"Tm"):
            string_line = lines[i].split()
            x = float(string_line[4])
            y = page_height - float(string_line[5])

            # Check if the current position is within a replacement height
            for replacement in replacements:
                if x > round(replacement[0], 3) and y >= replacement[1] and y <= replacement[3]:
                    continue

            # Check if the current position is within the height of the first redaction
            if x > first_redaction[0] and y >= first_redaction[1] and y <= first_redaction[3]:
                # Iterate through the lines to find the lines with text
                for j in range(i, len(lines)):
                    if lines[j].endswith(b"TJ") or lines[j].endswith(b"Tj"):
                        # Append the line information to the list of words to be repositioned
                        to_be_repositioned.append((lines[i], i, j))

    return to_be_repositioned

def _reposition_words_same_line(doc, to_be_repositioned, redactions, replacements, lines, xref):
    """
    Reposition the to-be-repositioned words based on the first redaction on the line.

    Parameters:
    - doc: The document.
    - to_be_repositioned: List of lines that need to be repositioned.
    - redactions: List of redaction rectangles.
    - replacements: List of replacement rectangles.
    - lines: List of lines in the PDF content.
    - xref: The xref of the page.

    Returns:
    - None
    """
    diff = 0

    # Iterate through each word to be repositioned
    for i in range(len(to_be_repositioned)):
        string_line = to_be_repositioned[i][0].split()
        x = float(string_line[4]) if len(string_line) > 4 else float(string_line[0])

        # Calculate the difference based on redactions and replacements
        for j in range(len(redactions)):
            if x >= redactions[j][2]:
                if replacements != []:
                    diff += (redactions[j][2] - redactions[j][0]) - replacements[j].width
                else:
                    diff += (redactions[j][2] - redactions[j][0])
            else:
                break

        # Calculate the new position of the word
        if (i > 0) or (len(redactions) > 1 and len(to_be_repositioned) == 1):
            new_pos = x - diff
        else:
            new_pos = redactions[0][0]

        # Update the x-coordinate in the string representation of the line
        if len(string_line) > 3:
            string_line[4] = str(new_pos).encode()
        else:
            string_line[0] = str(new_pos).encode()

        # Join the modified string line
        new_string = b" ".join(string_line)

        # Update the line in the list of lines
        lines[to_be_repositioned[i][1]] = new_string

        diff = 0

    # If there are words to be repositioned, update the stream in the document
    if len(to_be_repositioned) > 0:
        doc.update_stream(xref, b"\n".join(lines))

def _get_redaction_info(redaction, words_dict):
    """
    Get information about the redacted text, i.e., fontsize.

    Parameters:
    - redaction: Information about the redaction.
    - words_dict: Dictionary containing information about words, blocks, lines, and spans.

    Returns:
    - float: Fontsize of the redacted text.
    """
    block = redaction[5]
    line = redaction[6]

    # Adjust the block index if it's not the last block
    block = block if (block == len(words_dict['blocks']) - 1) else block + 1
    res = words_dict["blocks"][block]

    # Check if 'lines' information is present
    if 'lines' in res:
        # If the line is present in the block, use that information
        if line in res:
            res = words_dict["blocks"][block]["lines"][line]
        # If not, use the information of the first line in the block
        else:
            res = words_dict["blocks"][block]["lines"][0]
    else:
        # Return a default font size if 'lines' information is not present
        return 7.0

    # Check if 'spans' information is present
    if 'spans' in res:
        res = res['spans']

        # If there is only one span, use that information
        if len(res) == 1:
            res = res[0]
        # If there are multiple spans, find the span containing the redacted text
        else:
            for i in range(0, len(res)):
                if redaction[4] in res[i]['text']:
                    res = res[i]
                    break
    else:
        # Return a default font size if 'spans' information is not present
        return 7.0

    try:
        # Attempt to retrieve the font size from the span information
        fontsize = res['size']
    except TypeError:
        # If there is an issue with the data structure, use the font size from the first span
        fontsize = res[0]['size']

    return fontsize

def _add_replacements(redactions, page, words_dict, xref):
    """
    Add replacement texts for the specified redactions on a PDF page.

    Parameters:
    - redactions: List of redaction rectangles.
    - page: The PDF page.
    - words_dict: Dictionary containing information about words, blocks, lines, and spans.
    - xref: The xref of the page.

    Returns:
    - list: List of rectangles representing the areas occupied by the added replacement texts.
    """
    replacements_texts_rects = []

    # Iterate through each redaction
    for i in range(len(redactions)):
        # Get the font size information for the redaction
        fontsize = _get_redaction_info(redactions[i], words_dict)

        # Create a rectangle based on the redaction coordinates
        rect = fitz.Rect(redactions[i][0], redactions[i][1], redactions[i][2], redactions[i][3])

        # Insert replacement text into the redacted area and get the new rectangle
        new_rect = _insert_replacement_text(page, rect, fontsize)

        # Append the new rectangle to the list
        replacements_texts_rects.append(new_rect)

    return replacements_texts_rects

def _get_redactions_per_line(redactions, replacements):
    """
    Determine which redactions and replacements are on the same line (between the same y_0 and y_1).

    Parameters:
    - redactions: List of redaction rectangles.
    - replacements: List of replacement rectangles.

    Returns:
    - Tuple: Tuple containing dictionaries representing redactions per line, replacements per line, and lines per line.
    """
    redaction_per_line = {}
    replacements_per_line = {}
    lines_per_line = {}

    # Determine all redactions on a line, based on the y-coordinates.
    for i in range(len(redactions)):

        # Get y-coordinates for the line on which the redaction is on
        y_cords = (redactions[i][1], redactions[i][3])

        # If a redaction with y_cords is already present, add to redactions per line for y_cords
        if y_cords in redaction_per_line:
            redaction_per_line[y_cords].append(redactions[i])

            # If replacements are present, add to replacements per line for y_cords
            if replacements != []:
                replacements_per_line[y_cords].append(replacements[i])

        # If not, add new key-value pair.
        elif y_cords in lines_per_line:
            continue
        else:
            redaction_per_line[y_cords] = [redactions[i]]

            # If replacements are present, add to replacements per line for y_cords
            if replacements != []:
                replacements_per_line[y_cords] = [replacements[i]]
            else:
                replacements_per_line[y_cords] = []

    return (redaction_per_line, replacements_per_line)

def _get_command_lines_per_line(redactions, lines, redacts_to_textblocks, dim):
    """
    Identify lines of text associated with each redaction based on their y-coordinates.

    Parameters:
    - redactions: List of redaction rectangles.
    - lines: List of lines in the PDF content.
    - redacts_to_textblocks: Dictionary mapping redaction rectangles to text blocks.
    - dim: Tuple containing dimensions of the page (cropbox).

    Returns:
    - dict: Dictionary containing lines of text associated with each redaction's y-coordinates.
    """
    lines_per_line = {}

    # Iterate through each redaction
    for i in range(len(redactions)):
        # Get y-coordinates for the line on which the redaction is located
        y_cords = (redactions[i][1], redactions[i][3])

        # If y_cords not already in lines_per_line, add a new entry
        if y_cords not in lines_per_line:
            lines_per_line[y_cords] = [(redactions[i][0], redactions[i][2])]

            # Iterate through lines in the PDF content
            for j in range(len(lines)):
                # Check if the line is a transformation matrix (ends with b"Tm")
                if lines[j].endswith(b"Tm"):
                    x = float(lines[j].split()[4].decode())
                    y = dim[1] - float(lines[j].split()[5].decode())

                    # Create a rectangle representing the redaction
                    rect = fitz.Rect(redactions[i][0], redactions[i][1], redactions[i][2], redactions[i][3])

                    # Get the text block coordinates associated with the redaction
                    block_cords = redacts_to_textblocks[rect]

                    # Check if the current line is within the y-coordinates and text block coordinates
                    if y >= round(redactions[i][1], 3) and y <= round(redactions[i][3], 3) and \
                       y >= round(block_cords[1], 3) and y <= round(block_cords[3], 3) and \
                       x >= round(block_cords[0], 3) and x <= round(block_cords[2], 3):

                        # Iterate through subsequent lines until a TJ command is found
                        for q in range(j + 1, len(lines)):
                            if lines[q].endswith(b"TJ"):
                                lines_per_line[y_cords].append((lines[q], q, j))
                                break
                            elif lines[q].endswith(b"Tj"):
                                break

    return lines_per_line