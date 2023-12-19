import random


class LineManipulator:
    def __init__(self, lines_per_line, redactions_per_line, replacements_per_line, document_lines):
        self.lines_per_line = lines_per_line
        self.redactions_per_line = redactions_per_line
        self.replacements_per_line = replacements_per_line
        self.document_lines = document_lines

    def update_positions_lines(self):
        for lines in self.lines_per_line:
            red_cnt = len(self.redactions_per_line[lines])
            for line in self.lines_per_line[lines][1:]:
                text, res = line_decoder(line[0])
                new = line_encoder(lines, red_cnt, res, text, self.redactions_per_line, self.replacements_per_line)
                if new != None:
                    self.document_lines[line[1]] = new

        return self.document_lines


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

def line_encoder(lines, red_cnt, res, text, redaction_per_line, replacements_per_line):
    new_posadj =[]
    if len(res) > 1 and len(text) > 0:
        b = 1.0
        l = 0.0
        m = 0.0
        for q in res:
            if q == "":
                new_posadj.append("")
            # Find re-positions TODO: what if there are multiple really big or small positional adjustments.
            elif float(q) > 100 or float(q) < -100:
                l = redaction_per_line[lines][len(redaction_per_line[lines]) - red_cnt][2] - redaction_per_line[lines][len(redaction_per_line[lines]) - red_cnt][0]
                m = replacements_per_line[lines][len(redaction_per_line[lines]) - red_cnt].width
                b = (m/l)
                #print("OK", q, l, m, b)
                new_posadj.append(float(q) * (b if b != 0 else 1.0))
                red_cnt -= 1
            else:
                rand = random.uniform(0.2, 1.8)

                newnum = round(round(float(q) * 0.0042 * rand, 2) / 0.0042, 2)
                #print(q, newnum)
                new_posadj.append(newnum)

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
        #print(res, new)
        return new