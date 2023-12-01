import re
import fitz

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
        new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[2])
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
    return [words[5]]

def redact_example():
    redactor = DocumentRedactor("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/simple.pdf")
    pages = redactor.get_pages()
    for page in pages:
        redactor.prepare_page(page)
        dim = redactor.get_page_dimensions(page)
        (xref, lines, words) = redactor.get_page_contents(page)
        #redactor.remove_positional_adjustments(lines, xref)

        # Actual redactions
        redactions = select_multiple_redactions_example(words)

        # Add all redactions
        redactor.add_redactions(redactions, page)

        # Intermediate save with all to_be_redacted
        redactor.doc.save("res_temp.pdf")
        redactor.apply_redactions(page)

        xref, lines, words = redactor.get_page_contents(page)
        """
        print(lines)
        for i in range(len(lines)):
            if lines[i].endswith(b"TJ"):
                print(lines[i])
            if lines[i].endswith(b"Tj"):
                print("Tj", lines[i])

        """


        # insert text "x" for each redaction
        replacements_texts_rects = redactor.add_replacements(redactions, page)
        redactor.doc.save("res_temp2.pdf")

        page.clean_contents()

        xref, lines, words = redactor.get_page_contents(page)

        """pattern = re.compile(r'<[^>]+>|\([^)]+\)')
        for i in range(len(lines)):
            if lines[i].endswith(b"TJ"):
                if b"Tm" not in lines[i] or b"Tf" not in lines[i]:
                    #print("TJ FOUND", lines[i])
                    operands = lines[i].strip()[:-2].decode().strip()[1:-1]
                    res = re.sub(pattern, " ", operands).strip().split()
                    new = operands
                    #print(res)
                    if len(res) > 0:
                        for r in range(len(res)):
                            if r > 0:
                                new = new.replace(res[r], "-1")
                                operands = new
                            else:
                                #TODO calculate based on text
                                new = new.replace(res[r], "-300")
                                operands = new

                        lines[i] = b"[" + operands.encode() + b"]" + b" TJ"
                        #print("TJ FOUND AND POSITIONAL INFORMATION CHANGED")
                elif b"Tm" in lines[i] and b"Tf" in lines[i]:
                    #print(lines[i])
                    temp = lines[i].replace(b"Tm", b"Tm\n").replace(b"Tf", b"Tf\n").split(b"\n")
                    temp = [item.strip() for item in temp]

                    #\lines[i] = b""
                    lines[i] = b"\n ".join(temp)
                    #print(lines[i])



        redactor.doc.update_stream(xref, b"\n".join(lines))"""

        xref, lines, words = redactor.get_page_contents(page)

        #print(lines)
        # split redactions per line
        redaction_per_line = {}
        replacements_per_line = {}
        lines_per_line = {}
        for i in range(len(redactions)):
            # get y-cords aka which text line its on
            y_cords = (redactions[i][1], redactions[i][3])
            if y_cords in redaction_per_line:
                redaction_per_line[y_cords].append(redactions[i])
                replacements_per_line[y_cords].append(replacements_texts_rects[i])
            else:
                redaction_per_line[y_cords] = [redactions[i]]
                replacements_per_line[y_cords] = [replacements_texts_rects[i]]
                lines_per_line[y_cords] = [(redactions[i][0], redactions[i][2])]
                for j in range(len(lines)):
                    if lines[j].endswith(b"Tm"):
                        y = dim[1] - float(lines[j].split()[5].decode())
                        if y >= y_cords[0] and y <= y_cords[1]:
                            lines_per_line[y_cords].append((lines[j], j))
                        pass
                    elif lines[j].endswith(b"Td"):
                        pass

        # Loop over and select the right one
        print(lines_per_line)
        for i in lines_per_line:
            x = lines_per_line[i][0]
            red_cnt = len(redaction_per_line[i])

            # get candidates
            for j in range(1, len(lines_per_line[i]) - red_cnt):
                print(j)
                if j == len(lines_per_line[i]) - red_cnt - 1:
                    final = lines_per_line[i][j]
                    print("Final (last item)", final[0], final[1], lines[final[1]+1])
                    break
                elif j > 1:
                    if x[0] > float(lines_per_line[i][j-1][0].split()[4]) and x[0] < float(lines_per_line[i][j][0].split()[4]):
                        print("Final", lines_per_line[i][j-1][0], lines_per_line[i][j-1][1], lines[lines_per_line[i][j-1][1] + 1])
                        break

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