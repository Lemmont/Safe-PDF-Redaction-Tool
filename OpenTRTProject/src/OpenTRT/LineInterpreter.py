import random


class LineManipulator:
    def __init__(self, lines_per_line, redactions_per_line, replacements_per_line, document_lines):
        """
        Initialize a LineManipulator object.

        Parameters:
        - lines_per_line: Dictionary containing lines of text associated with each redaction's y-coordinates.
        - redactions_per_line: Dictionary containing redactions associated with each line's y-coordinates.
        - replacements_per_line: Dictionary containing replacements associated with each line's y-coordinates.
        - document_lines: List of lines in the document.
        """
        self.lines_per_line = lines_per_line
        self.redactions_per_line = redactions_per_line
        self.replacements_per_line = replacements_per_line
        self.document_lines = document_lines

    def update_positions_lines(self):
        """
        Update positions of lines based on redactions and replacements.

        Returns:
        - list: List of updated lines.
        """
        has_been_changed = []

        to_be_skipped = []
        document_lines_temp = self.document_lines


        special_lines = {}
        red_cnt_map = {}
        red_cnt = 0

        for lines in self.lines_per_line:
            red_cnt = len(self.redactions_per_line[lines]) # amount of redactions on this page

            for item in self.lines_per_line[lines][1:]:
                special_lines[item[0]] = lines
                red_cnt_map[item[0]] = red_cnt

        # Loop over all operations on this page.
        for line in range(0, len(document_lines_temp)):

            if document_lines_temp[line].endswith(b"TJ"):
                text, res = line_decoder(document_lines_temp[line])
                #print(text, res)
                if document_lines_temp[line] in special_lines:
                    new_line = line_encoder(special_lines[document_lines_temp[line]], red_cnt_map[document_lines_temp[line]], res, text, self.redactions_per_line, self.replacements_per_line)
                else:
                    new_line = line_encoder((0,0), 0, res, text, self.redactions_per_line, self.replacements_per_line)
                # print("new", new_line)
                if new_line is not None:
                    if len(res) > 1:
                        has_been_changed.append(new_line)
                    self.document_lines[line] = new_line


        # Edit all other lines

        if len(has_been_changed) > 0:
            return (self.document_lines, True)
        else:
            return (self.document_lines, False)


def line_decoder(line):
    """
    Decode a PDF content line, extracting text and numerical information.

    Parameters:
    - line: PDF content line to be decoded.

    Returns:
    - tuple: A tuple containing lists of text and numerical information.
    """
    item = line.strip()[:-2].strip()[1:-1].decode()
    status = 0
    text_list = []
    num_list = []
    text_string = ""
    num_string = ""

    # Iterate through each character in the line
    for h in item:
        if status == 0 and (h == "(" or h == "<"):
            # Begin processing text
            text_string += h

            # If there was numerical information before, add it to the num_list
            if num_string != "":
                num_list.append(num_string)
                num_string = ""

            # Change status to text processing
            status = 1
        elif status == 0:
            # Continue processing numerical information
            num_string += h
        elif status == 1 and (h == ")" or h == ">"):
            # End processing text
            text_string += h

            # Append text and an empty string to num_list
            text_list.append(text_string)
            num_list.append("")

            # Reset text_string and change status to numerical processing
            text_string = ""
            status = 0
        elif status == 1 and h != "\\":
            # Continue processing text
            text_string += h
        elif status == 1 and h == "\\":
            # Handle escape character by moving to escape status
            text_string += h
            status = 2
        elif status == 2 and h not in [")", "(", "<", ">"]:
            # Continue processing escaped characters
            text_string += h
        elif status == 2 and (h == ")" or h == "(" or h == "<" or h == ">"):
            # End processing escaped characters
            text_string += h

            # Change status back to text processing
            status = 1

    # Return a tuple containing text and numerical lists
    return (text_list, num_list)

def line_encoder(lines, red_cnt, res, text, redaction_per_line, replacements_per_line):
    """
    Encode text and positional information based on certain conditions.

    Parameters:
    - lines: The line number.
    - red_cnt: The redaction count.
    - res: List of positional information.
    - text: List of text.
    - redaction_per_line: Dictionary of redactions per line.
    - replacements_per_line: Dictionary of replacements per line.

    Returns:
    - bytes: Encoded line.
    """
    new_posadj = []

    # Check if there is positional and text information to encode
    if len(res) > 1 and len(text) > 0:
        b = 1.0
        l = 0.0
        m = 0.0

        # Iterate through each positional information in res
        for q in res:
            if q == "":
                # If no positional information, append an empty string to new_posadj
                new_posadj.append("")
            # Find re-positions
            elif float(q) > 100 or float(q) < -100:
                if lines in replacements_per_line and replacements_per_line[lines] != []:
                    # Calculate new positional adjustment based on replacements
                    l = redaction_per_line[lines][len(redaction_per_line[lines]) - red_cnt][2] - redaction_per_line[lines][len(redaction_per_line[lines]) - red_cnt][0]
                    m = replacements_per_line[lines][len(redaction_per_line[lines]) - red_cnt].width
                    b = (m / l)
                    # print(m, l, q)

                    new_posadj.append(float(q) * (b if b != 0 else ""))
                    red_cnt -= 1
                else:
                    # If no replacements, append 0 to new_posadj
                    new_posadj.append("")
            else:
                new_posadj.append("")

        new = b"["
        t_index = 0

        # Iterate through each positional information in res
        for m in range(len(res)):
            if res[m] == "":
                # If no positional information, append the corresponding text to new
                new += str(text[t_index]).encode()
                t_index += 1
            else:
                if m != len(res) - 1:
                    # Append the new positional adjustment to new
                    new += str(new_posadj[m]).encode()

        # print(res, new)

        new += b"] TJ"
        return new