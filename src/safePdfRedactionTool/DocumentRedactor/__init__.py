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
        new_length = font.text_length("x")
        newx1 = rect[1] + new_length + 5
        print(rect, newx1, new_length)
        new_rect = fitz.Rect(rect[0], rect[1], newx1, rect[2])
        page.insert_textbox(new_rect, "x", fontname="times-roman", fontsize=12)
        return new_rect

    def get_to_be_repositioned_words(self, page_height, lines, first_redaction: fitz.Rect, replacements):
        to_be_repositioned = []
        for i in range(len(lines)):
            if lines[i].endswith(b"Tm"):
                string_line = lines[i].split()
                x = float(string_line[4])
                y = page_height - float(string_line[5])
                if x >= first_redaction[0] and  y >= first_redaction[1] and y <= first_redaction[3]:
                    to_be_repositioned.append((lines[i], i))
            elif lines[i].endswith(b"Td"):
                string_line = lines[i].split()
                x = float(string_line[0])
                y = page_height - float(string_line[1])
                print(lines[i], replacements, y)
                if first_redaction[0] <= x and  first_redaction[1] <= y  and first_redaction[3] >= y :
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
        length = 0.0
        count = 0
        for i in range(len(to_be_repositioned)):
            string_line = to_be_repositioned[i][0].split()
            x = float(string_line[4]) if len(string_line) > 4 else float(string_line[0])
            if count >= 1:
                length += float(to_be_repositioned[i - 1][0].split()[4]) - x
                new_pos = redactions[0][0] - length
            else:
                new_pos = redactions[0][0]

            value = 0.0

            for j in range(1, len(redactions)):
                if x >= redactions[j][0]:
                    if j < len(redactions) -1:
                        value += redactions[j][2] - redactions[j][0]
                    elif j == len(redactions) - 1:
                        value += redactions[j][2] - redactions[j][0]
                else:
                    break


            new_pos -= value

            if len(string_line) > 3:
                string_line[4] = str(new_pos).encode()
            else:
                string_line[0] = str(new_pos).encode()

            new_string = b" ".join(string_line)
            lines[to_be_repositioned[i][1]] = new_string

            count += 1
        self.doc.update_stream(xref, b"\n".join(lines))

    def finalize_redactions(self, new_filename="res.pdf"):
        self.doc.save(new_filename)
        self.doc.close()
