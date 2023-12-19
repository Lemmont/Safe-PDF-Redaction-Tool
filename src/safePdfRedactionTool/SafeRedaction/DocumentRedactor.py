import logging
import fitz
import xml.etree.ElementTree as ET
from . import LineInterpreter as Li
from typing import Dict

logger = logging.getLogger(__name__)

class DocumentRedactor:
    def __init__(self, document):
        self.doc: fitz.Document = fitz.open(document, filetype="pdf")

        # Check if file given is valid. Otherwise raise error
        if self.doc.page_count == 0:
            raise ValueError("No file given or not a valid file.")

        self.pages = []
        self.redactions: Dict = None
        self.replacements_per_page = {}
        self.words_dict: Dict = None
        self.redacts_textblocks_per_page = {}

        self.pages = [page for page in self.doc.pages()]


    def __str__(self) -> str:
        msg = "--- REDACTOR ---\n"
        if self.doc:
            msg += "\n-- File Information --\n"
            msg += " name        " + self.doc.name + "\n"
            msg += " pages       " + str(self.doc.page_count) + "\n"
            msg += " emb. files  " + str(self.doc.embfile_count()) + "\n"
        else:
            msg += "No (valid) file inserted\n"

        return msg

    def get_word_count(self):
        """
            Get occurence of every word in document.
        """
        words = {}
        for page in self.doc.pages():
            page_words = page.get_text("words", sort=True)
            for i in page_words:
                if i[4] in words:
                    words[i[4]] += 1
                else:
                    words[i[4]] = 1

        return words

    def get_metadata(self):
        return self.doc.metadata


    def add_redactions(self, redactions=None):
        if redactions == None or redactions == {}:
            print("no redactions")
            return

        # TODO maybe check redactions comming in
        self.redactions = redactions
        for page in self.pages:

            # check if there are redactions
            page_redactions = self.redactions[page]
            xref, lines, words, text_blocks = _get_page_contents(page)
            redacts_to_textblocks = _get_redactions_to_textblock(page_redactions, text_blocks)
            self.redacts_textblocks_per_page[page] = redacts_to_textblocks

            for redaction in page_redactions:
                rect = fitz.Rect(redaction[0], redaction[1], redaction[2], redaction[3])

                # Make the redact annotation small so that no other text is selected
                h = rect.height
                my = (rect.y0 + rect.y1) / 2
                y0 = my - h * 0.1
                y1 = my + h * 0.1
                rect.y0 = y0
                rect.y1 = y1

                # Add redaction
                self.add_redaction(page, rect)


    def apply_redactions_without_replacements(self):
        if self.redactions == None or self.redactions == {}:
            print("No redactions to be removed")
            return

        for page in self.pages:
            _apply_redactions(page)


    def apply_redactions_with_replacements(self):
        if self.redactions == None or self.redactions == {}:
            print("No redactions")
            return

        for page in self.pages:
            page_redactions = self.redactions[page]

            self.words_dict = page.get_text("dict")
            xref, lines, words, text_blocks = _get_page_contents(page)

            _apply_redactions(page)
            replacements_texts_rects = _add_replacements(page_redactions, page, self.words_dict, xref)
            self.replacements_per_page[page] = replacements_texts_rects

    def edit_positional_information(self):
        if self.redactions == None or self.redactions == {}:
            print("No redactions")
            return

        for page in self.pages:
            page_redactions = self.redactions[page]
            page_replacements = self.replacements_per_page[page]
            page_redacts_to_textblocks = self.redacts_textblocks_per_page[page]

            dim = _get_page_dimensions(page)

            _clean_page(page)
            xref, lines, words, text_blocks = _get_page_contents(page)
            redaction_per_line, replacements_per_line = _get_redactions_per_line(page_redactions, page_replacements)
            lines_per_line = _get_command_lines_per_line(page_redactions, lines, page_redacts_to_textblocks, dim)
            Manipulator = Li.LineManipulator(lines_per_line, redaction_per_line, replacements_per_line, lines)

            new = Manipulator.update_positions_lines()

            self.doc.update_stream(xref, b"\n".join(new))

            xref, lines, words, text_blocks = _get_page_contents(page)
            for i in redaction_per_line:
                redactions_on_line = redaction_per_line[i]
                replacements_on_line = replacements_per_line[i]
                to_be_repositioned = _get_to_be_repositioned_words(dim[1], lines, redactions_on_line[0], replacements_on_line)
                _reposition_words_same_line(self.doc, to_be_repositioned, redactions_on_line, replacements_on_line, lines, xref)

        self.pages = [page for page in self.doc.pages()]

    def add_redaction(self, page: fitz.Page, rect:fitz.Rect):
        """
            Add redaction to defined rect.
        """
        page.add_redact_annot(rect.quad)

    def finalize_redactions(self, redactions, new_filename="redacted.pdf"):
        self.doc.save(new_filename)
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

def _apply_redactions(page:fitz.Page):
        """
            Apply all redactions to a page.
        """
        page._apply_redactions()

def _get_page_dimensions(page: fitz.Page):
        """
            Get cropbox/dimensions of page
        """
        cropbox = page.cropbox
        return (cropbox.x1, cropbox.y1)

def _get_redactions_to_textblock(redactions, text_blocks):
    """
        Determine in which text_block a redaction is situated
    """
    redacts_to_textblocks = {}
    for i in redactions:
        redact_rect = fitz.Rect(i[0], i[1], i[2], i[3])
        for j in text_blocks:
            if j.contains(redact_rect):
                redacts_to_textblocks[redact_rect] = j

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
                diff += (redactions[j][2]-redactions[j][0]) - replacements[j].width
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
            replacements_per_line[y_cords].append(replacements[i])

        # If not, add new key-value pair.
        elif y_cords in lines_per_line:
            continue
        else:
            redaction_per_line[y_cords] = [redactions[i]]
            replacements_per_line[y_cords] = [replacements[i]]

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