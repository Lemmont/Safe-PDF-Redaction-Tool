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
        return (xref, lines, words)

    def get_redact_annots(self, page: fitz.Page):
        pass

    def get_words_in_annot(self, annot: fitz.Rect):
        pass

    def add_redact_annot(self, page: fitz.Page, rect: fitz.Rect):
        page.add_redact_annot(rect.quad)

    def apply_redactions(self, page: fitz.Page):
        page._apply_redactions()

    def get_word_bbox(self, word: str):
        pass

    def insert_replacement_text(self, page: fitz.Page, rect: fitz.Rect):
        """
            Insert replacement text in rect. of redacted text

            FOR NOW ONLY "x"
        """
        font = fitz.Font("times-roman")
        #print(font.text_length("x"))
        new_length = font.text_length("redacted", 8)
        newx1 = rect[0] + new_length
        new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[3])
        #print(new_rect)
        page.insert_textbox(new_rect, "redacted", fontname="times-roman", fontsize=8)
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
                    to_be_repositioned.append((lines[i], i))
            elif lines[i].endswith(b"Td"):
                temp = False
                string_line = lines[i].split()
                x = float(string_line[0])
                y = page_height - float(string_line[1])
                for replacement in replacements:
                    #print(replacement, x, y)
                    if x >= round(replacement[0], 3) and y >= replacement[1] and y <= replacement[3]:
                        temp = True
                if first_redaction[0] < x and  first_redaction[1] <= y  and first_redaction[3] >= y :
                    to_be_repositioned.append((lines[i], i))

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

                """
                #TODO: what if not divided by \n?
                if b"Tm" in lines[i] or b"Tf" in lines[i]:
                    temp = lines[i].replace(b"Tm", b"Tm\n").replace(b"Tf", b"Tf\n").split(b"\n")
                    temp = [i.strip() for i in temp]
                    temp[-1] = res_text.encode()
                    lines[i] = b"\n ".join(temp)
                else:

                    lines[i] = res_text.encode()
                """
                lines[i] = res_text.encode()


        self.doc.update_stream(xref, b"\n".join(lines))

    def reposition_words_same_line(self, to_be_repositioned, redactions, replacements, lines, xref):
        """
            Reposition the to be repositioned words based on the first redaction
            on the line.
        """
        length = redactions[0][2] - redactions[0][0]
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

            if i > 0:
                new_pos = x - diff
            else:
                new_pos = redactions[0][0]

            if len(string_line) > 3:
                string_line[4] = str(new_pos).encode()
            else:
                string_line[0] = str(new_pos).encode()

            new_string = b" ".join(string_line)
            #print(x, new_string)
            lines[to_be_repositioned[i][1]] = new_string

            diff = 0
        if len(to_be_repositioned) > 0:
            self.doc.update_stream(xref, b"\n".join(lines))

    def finalize_redactions(self, new_filename="res.pdf"):
        self.doc.save(new_filename)
        self.doc.close()

    def add_redactions(self, redactions, page):
        for redaction in redactions:
            rect = fitz.Rect(redaction[0], redaction[1], redaction[2], redaction[3])
            self.add_redact_annot(page, rect)

    def add_replacements(self, redactions, page):
        replacements_texts_rects = []
        for i in range(len(redactions)):
            rect = fitz.Rect(redactions[i][0], redactions[i][1] -5 , redactions[i][2], redactions[i][3])
            new_rect = self.insert_replacement_text(page, rect)
            replacements_texts_rects.append(new_rect)
        return replacements_texts_rects

def select_multiple_redactions_example(words):
    return [words[4], words[7], words[15], words[18]]

def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/custom4.pdf")
    pages = redactor.get_pages()
    for page in pages:
        redactor.prepare_page(page)
        dim = redactor.get_page_dimensions(page)
        xref, lines, words = redactor.get_page_contents(page)

        # Text blocks
        text_blocks: list[rect] = []
        blocks = page.get_text("blocks", sort=True)
        for i in range(len(blocks)):
            # [0:4]: b-boxes of text blocks.
            rect = fitz.Rect(blocks[i][0], blocks[i][1], blocks[i][2], blocks[i][3])
            text_blocks.append(rect)

        # The (test) redactions (for this page)
        redactions = select_multiple_redactions_example(words)

        # Determine in which text_block the redactions are situated:
        redacts_to_textblocks = {}
        for i in redactions:
            redact_rect = fitz.Rect(i[0], i[1], i[2], i[3])
            for j in text_blocks:
                if j.contains(redact_rect):
                    redacts_to_textblocks[redact_rect] = j

        # Add all redactions to document
        redactor.add_redactions(redactions, page)

        # Intermediate save with all to_be_redacted
        redactor.doc.save("res_temp.pdf")

        # Apply redactions to document/page
        redactor.apply_redactions(page)

        # Get (new) page content
        xref, lines, words = redactor.get_page_contents(page)

        # Insert text ("x") for each redaction
        replacements_texts_rects = redactor.add_replacements(redactions, page)

        # Intermediate save with all insertions.
        redactor.doc.save("res_temp2.pdf")

        # Clean contents of page.
        page.clean_contents()

        # Get (new) page content
        xref, lines, words = redactor.get_page_contents(page)

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
                replacements_per_line[y_cords].append(replacements_texts_rects[i])

            # If not, add new key-value pair.
            elif y_cords in lines_per_line:
                continue
            else:
                redaction_per_line[y_cords] = [redactions[i]]
                replacements_per_line[y_cords] = [replacements_texts_rects[i]]


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
                        #print(x, y, redactions[i])
                        if y >= round(redactions[i][1], 3) and y <= round(redactions[i][3]) and y >= round(block_cords[1], 3) and y <= round(block_cords[3], 3) and x >= round(block_cords[0], 3) and x <= round(block_cords[2], 3):
                            #print("YES", lines[j], redactions[i], block_cords, round(block_cords[0], 3))
                            for q in range(j + 1, len(lines)):
                                if lines[q].endswith(b"TJ"):
                                    lines_per_line[y_cords].append((lines[q], q, j))
                                    #print(lines[q])
                                    break
                                elif lines[q].endswith(b"Tj"):
                                    #print(lines[q])
                                    break

        pattern = re.compile(r'\((?:[^()]|\([^()]*\))*\)|<(?:[^<>]|<[^<>]*>)*>')
        #print(lines_per_line)
        for i in lines_per_line:
            red_cnt = len(redaction_per_line[i])
            x_cords = lines_per_line[i][0]
            new_posadj = []
            print(len(lines_per_line[i][1:]), lines_per_line[i][1:], red_cnt)
            for j in lines_per_line[i][1:]:

                print("OK", j, x_cords, "\n")
                item = j[0].strip()[:-2].strip()[1:-1].decode()
                res = pattern.sub(' ', item).strip().split()
                text = pattern.findall(item)
                #print("res", res, "item", text)
                print(item)
                if len(res) > 0 and len(text) > 0:
                    print(res)
                    for q in res:
                        # find re-positions
                        print(q)
                        if float(q) > 100 or float(q) < -100:
                            print(red_cnt)
                            l = redaction_per_line[i][len(redaction_per_line[i]) - red_cnt][2] - redaction_per_line[i][len(redaction_per_line[i]) - red_cnt][0]
                            m = replacements_per_line[i][len(redaction_per_line[i]) - red_cnt].width
                            #print("check", l,m, m / l)
                            new_posadj.append(float(q) * (m/l) * random.uniform(0.95, 1.05))
                            # change based on replacement
                            red_cnt -= 1
                        else:
                            rand = random.uniform(0.5, 1.9)
                            new_posadj.append(float(q) * rand)


                    #print(len(text), len(new_posadj))
                    new = b"["
                    for m in range(len(text)):
                        new += str(text[m]).encode()

                        if m != len(text) - 1:
                            new += str(new_posadj[m]).encode()
                    new += b"] TJ"

                    #print(new)
                    lines[j[1]] = new
                """
                elif len(res) == 0 and len(text) == 1:
                    if text[0][1:-1] != " ":
                        if red_cnt == len(redaction_per_line[i]):
                            red_cnt -= 1
                        elif red_cnt > 0:
                            tm_line = lines[j[2]]
                            x = float(lines[j[2]].split()[4].decode())
                            new_x = x #- replacements_per_line[i][(-red_cnt + len(redaction_per_line[i]))].width # based on -redaction + replacement
                            lines[j[2]] = tm_line.replace(str(x).encode(), str(new_x).encode())
                            red_cnt -= 1
                """

        redactor.doc.update_stream(xref, b"\n".join(lines))
        xref, lines, words = redactor.get_page_contents(page)

        xref, lines, words = redactor.get_page_contents(page)
        for i in redaction_per_line:
            redactions_on_line = redaction_per_line[i]
            replacements_on_line = replacements_per_line[i]

            # what if we only use the lines which are the same as the y cords of the redacted items per line?
            # That way we can also check the TJ(s) of that line!
            to_be_repositioned = redactor.get_to_be_repositioned_words(dim[1], lines, redactions_on_line[0], replacements_on_line)
            redactor.reposition_words_same_line(to_be_repositioned, redactions_on_line, replacements_on_line, lines, xref)

        xref, lines, words = redactor.get_page_contents(page)
        #print(lines)
        redactor.finalize_redactions()