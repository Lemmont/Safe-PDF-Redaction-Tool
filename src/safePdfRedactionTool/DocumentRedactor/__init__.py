import re
import fitz
import random

class DocumentRedactor:
    def __init__(self, document):
        self.doc: fitz.Document = fitz.open(document, filetype="pdf")

    def get_pages(self):
        """
            Get pages of document
        """
        return [page for page in self.doc]

    def prepare_page(self, page: fitz.Page):
        page.clean_contents()

    def get_page_dimensions(self, page: fitz.Page):
        """
            Get cropbox/dimensions of page
        """
        cropbox = page.cropbox
        return (cropbox.x1, cropbox.y1)

    def get_page_contents(self, page: fitz.Page):
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

    def add_redact_annot(self, page: fitz.Page, rect: fitz.Rect):
        """
            Add redaction to defined rect.
        """
        page.add_redact_annot(rect.quad)

    def apply_redactions(self, page: fitz.Page):
        """
            Apply all redactions to a page.
        """
        page._apply_redactions()


    def insert_replacement_text(self, page: fitz.Page, rect: fitz.Rect, fontsize):
        """
            Insert replacement text in rect. of redacted text

            FOR NOW ONLY placeholder
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

    def get_to_be_repositioned_words(self, page_height, lines, first_redaction: fitz.Rect, replacements):
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

    def remove_positional_adjustments(self, lines, xref):
        """
            Remove positional adjustments from operand of TJ operator
            and update the lines.
        """
        angle_bracket_pattern = re.compile(r'<(.*?)>|\((.*?)\)')
        for i in range(len(lines)):
            if lines[i].endswith(b"TJ"):
                operands = lines[i][:-2].strip().decode()
                text = angle_bracket_pattern.findall(operands)
                res_text = "["
                #print(text)
                for t in text:
                    if t[0] == '':
                        res_text = res_text + "(" + t[1] + ")"
                    elif t[1] == '':
                        res_text = res_text + "<" + t[0] + ">"
                res_text += "]TJ"

                lines[i] = res_text.encode()


        self.doc.update_stream(xref, b"\n".join(lines))

    def reposition_words_same_line(self, to_be_repositioned, redactions, replacements, lines, xref):
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
            self.doc.update_stream(xref, b"\n".join(lines))

    def finalize_redactions(self, new_filename="redacted.pdf"):
        self.doc.save(new_filename)
        self.doc.close()

    def add_redactions(self, redactions, page):
        for redaction in redactions:
            rect = fitz.Rect(redaction[0], redaction[1], redaction[2], redaction[3])

            # Make the redact annotation small so that no other text is selected
            h = rect.height
            my = (rect.y0 + rect.y1) / 2
            y0 = my - h * 0.1
            y1 = my + h * 0.1
            rect.y0 = y0
            rect.y1 = y1

            self.add_redact_annot(page, rect)

    def get_redaction_info(self, redaction, words_dict):
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
            return 9.0

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
            print("NO SPANS","\n", res)
            return 9.0

        try:
            fontsize = res['size']
        except TypeError:
            fontsize = res[0]['size']

        return fontsize


    def add_replacements(self, redactions, page, words_dict, xref):
        replacements_texts_rects = []
        for i in range(len(redactions)):
            fontsize = self.get_redaction_info(redactions[i], words_dict)
            rect = fitz.Rect(redactions[i][0], redactions[i][1] , redactions[i][2], redactions[i][3] )
            new_rect = self.insert_replacement_text(page, rect, fontsize)
            replacements_texts_rects.append(new_rect)
        return replacements_texts_rects

    def redactions_to_textblock(self, redactions, text_blocks):
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

    def redactions_per_line(self, redactions, replacements):
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

    def command_lines_per_line(self, redactions, lines, redacts_to_textblocks, dim):
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

def select_multiple_redactions_example(words):
    words_list = []
    b = []
    for i in range(random.randint(1, 20)):
        a = random.randint(0, len(words) - 1)
        if a not in b:
            b.append(a)

    b.sort()
    for j in b:
        words_list.append(words[j])


    return words_list

def line_decoder(line):
    item = line.strip()[:-2].strip()[1:-1].decode()
    status = 0
    text_list = []
    num_list = []
    text_string = ""
    num_string = ""
    #TODO: what if (> or (> or <( etc.
    for h in item:
        if status == 0 and (h == "(" or h == "<"):
            text_string += h
            if num_string != "":
                num_list.append(num_string)
                num_string = ""
            status = 1
        elif status == 0:
            num_string += h
        elif status == 1 and (h == ")" or h == ">"):
            text_string += h
            text_list.append(text_string)
            num_list.append("")
            text_string = ""
            status = 0
        elif status == 1 and h != "\\":
            text_string += h
        elif status == 1 and h == "\\":
            text_string += h
            status = 2
        elif status == 2 and h not in [")", "(", "<", ">"]:
            text_string += h
        elif status == 2 and (h == ")" or h == "(" or h == "<" or h == ">"):
            text_string += h
            status = 1

    return (text_list, num_list)

def line_encoder(i, red_cnt, res, text, redaction_per_line, replacements_per_line):
    new_posadj =[]
    if len(res) > 1 and len(text) > 0:
        for q in res:
            if q == "":
                new_posadj.append("")
            # Find re-positions
            elif float(q) > 100 or float(q) < -200:
                l = redaction_per_line[i][len(redaction_per_line[i]) - red_cnt][2] - redaction_per_line[i][len(redaction_per_line[i]) - red_cnt][0]
                m = replacements_per_line[i][len(redaction_per_line[i]) - red_cnt].width
                b = m/l
                new_posadj.append(float(q) * (b if b != 0 else 1.0) * random.uniform(0.95, 1.05))
                red_cnt -= 1
            else:
                rand = random.uniform(0.8, 1.2)
                new_posadj.append(float(q) * rand)

        new = b"["
        t_index = 0
        for m in range(len(res)):
            if res[m] == "":
                new += str(text[t_index]).encode()
                t_index += 1
            else:
                if m != len(res) - 1:
                    new += str(new_posadj[m]).encode()
        new += b"] TJ"
        return new

def generate_redactions_per_page(redactor: DocumentRedactor, pages):
    redactions_per_page = {}
    for page in pages:
        redactor.prepare_page(page)
        xref, lines, words, text_blocks = redactor.get_page_contents(page)
        redactions = select_multiple_redactions_example(words)
        redactions_per_page[page] = redactions

    return redactions_per_page

def redact_step_1(redactor: DocumentRedactor, pages, redactions):
    """
        Add redactions to a document and save a temporary file
    """
    redacts_textblocks_per_page = {}
    for page in pages:
        # Get redactions of this page
        page_redactions = redactions[page]

        # Get info of the page
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Determine mapping of redactions of this page to the text_blocks of this page.
        redacts_to_textblocks = redactor.redactions_to_textblock(page_redactions, text_blocks)

        redacts_textblocks_per_page[page] = redacts_to_textblocks

        # Add all redactions to document
        redactor.add_redactions(page_redactions, page)

    redactor.doc.save("to-be-redacted.pdf")

    return redacts_textblocks_per_page

def redact_step_2(redactor: DocumentRedactor, pages, redactions):
    """
        Add replacement text to a document and save a temporary file
    """
    replacements_per_page = {}
    for page in pages:
        # Get redactions of this page
        page_redactions = redactions[page]

        # Get word dict with extra info
        words_dict = page.get_text("dict")

        # Get page contents
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Apply redactions
        redactor.apply_redactions(page)

        # Add replacements and return the replacements
        replacements_texts_rects = redactor.add_replacements(page_redactions, page, words_dict, xref)
        replacements_per_page[page] = replacements_texts_rects

    # Save
    redactor.doc.save("replaced-redactions.pdf")

    # Return replacements
    return replacements_per_page

def redact_step_3(redactor: DocumentRedactor, pages, redactions, replacements, redacts_textblocks):
    """
        Remove white spaces, repositon text and edit positional data.
    """
    for page in pages:

        # Get page redactions, replacements and to-textblock mapping for this page.
        page_redactions = redactions[page]
        page_replacements = replacements[page]
        page_redacts_to_textblocks = redacts_textblocks[page]

        # Get dimensions of page.
        dim = redactor.get_page_dimensions(page)

        # Clean this page's objects.
        page.clean_contents()

        # Get page info.
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Get redaction per line.
        redaction_per_line, replacements_per_line = redactor.redactions_per_line(page_redactions, page_replacements)

        # Get internal pdf command lines per line.
        lines_per_line = redactor.command_lines_per_line(page_redactions, lines, page_redacts_to_textblocks, dim)

        # Update complex text rendering (TJ) positioning.
        for i in lines_per_line:
            red_cnt = len(redaction_per_line[i])
            for j in lines_per_line[i][1:]:

                # Decode line
                text, res = line_decoder(j[0])

                # Encode line
                new = line_encoder(i, red_cnt, res, text, redaction_per_line, replacements_per_line)
                if new != None:
                    lines[j[1]] = new

        redactor.doc.update_stream(xref, b"\n".join(lines))

        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Update text line (Tm) position.
        for i in redaction_per_line:
            redactions_on_line = redaction_per_line[i]
            replacements_on_line = replacements_per_line[i]
            to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, redactions_on_line[0], replacements_on_line)
            redactor.reposition_words_same_line(to_be_repositioned, redactions_on_line, replacements_on_line, lines, xref)

        # TODO: optional noise to positional information throughout the page


def redact_file(file):
    redactor = DocumentRedactor(file)
    pages = redactor.get_pages()

    # Generate (random) redactions for each page in file, in order from top-left to bottom-right.
    redactions = generate_redactions_per_page(redactor, pages)

    # Do the first redaction step: highlight the to-be-redacted-text in the document.
    redacts_textblocks_per_page = redact_step_1(redactor, pages, redactions)

    # Do the second redaction step: replace the to-be-redacted text items with new text
    replacements_per_page = redact_step_2(redactor, pages, redactions)

    # Do the third redaction step: remove whitespaces, reposition text and edit positional data
    redact_step_3(redactor, pages, redactions, replacements_per_page, redacts_textblocks_per_page)\

    redactor.finalize_redactions()


def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/staatslot.pdf")
    pages = redactor.get_pages()
    for page in pages:
        # Get word dict with extra info
        words_dict = page.get_text("dict")
        redactor.prepare_page(page)
        dim = redactor.get_page_dimensions(page)
        xref, lines, words, text_blocks = redactor.get_page_contents(page)
        # The (test) redactions (for this page)
        redactions = select_multiple_redactions_example(words)

        # Determine in which text_block the redactions are situated:
        redacts_to_textblocks = redactor.redactions_to_textblock(redactions, text_blocks)

        # Add all redactions to document
        redactor.add_redactions(redactions, page)

        # Intermediate save with all to_be_redacted
        redactor.doc.save("res_temp.pdf")

        # Apply redactions to document/page
        redactor.apply_redactions(page)

        # Get (new) page content
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Insert text ("x") for each redaction
        replacements_texts_rects = redactor.add_replacements(redactions, page, words_dict, xref)

        # Intermediate save with all insertions.
        redactor.doc.save("res_temp2.pdf")

        # Clean contents of page.
        page.clean_contents()

        # Get (new) page content
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        redaction_per_line, replacements_per_line = redactor.redactions_per_line(redactions, replacements_texts_rects)
        lines_per_line = redactor.command_lines_per_line(redactions, lines, redacts_to_textblocks, dim)


        # Update complex text rendering (TJ) positioning
        for i in lines_per_line:
            red_cnt = len(redaction_per_line[i])
            for j in lines_per_line[i][1:]:

                # Decode line
                text, res = line_decoder(j[0])

                # Encode line
                new = line_encoder(i, red_cnt, res, text, redaction_per_line, replacements_per_line)
                if new != None:
                    lines[j[1]] = new

        redactor.doc.update_stream(xref, b"\n".join(lines))
        xref, lines, words, text_blocks = redactor.get_page_contents(page)

        # Update text line (Tm) position
        for i in redaction_per_line:
            redactions_on_line = redaction_per_line[i]
            replacements_on_line = replacements_per_line[i]
            to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, redactions_on_line[0], replacements_on_line)
            redactor.reposition_words_same_line(to_be_repositioned, redactions_on_line, replacements_on_line, lines, xref)

    redactor.finalize_redactions()