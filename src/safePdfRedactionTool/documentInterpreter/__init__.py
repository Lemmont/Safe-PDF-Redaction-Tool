from typing import Dict
import fitz
import re
import codecs

class DocumentInterpreter:
    def __init__(self, document: fitz.Document, pages: Dict[int, fitz.Page], fonts: Dict[int, str], contents):
        self.doc: fitz.Document = document
        self.pages: Dict[int, any] = pages # TO BE EDITED
        self.fonts: Dict[int, Dict[str, any]] = fonts # TO BE EDITED
        self.contents = contents

    def parse_character_mapping(self, page_fonts: Dict[str, any]):
        """
            Get character mapping of fonts on page

            :param page_fonts: fonts of a page
            :return: dictonary of character mappings
        """
        pattern = re.compile(r'beginbfchar\s*\n(.*?)(?=\nendbfchar)', re.DOTALL)
        fonts_mapping = {}

        # Loop over the fonts
        for page_font in page_fonts.items():

            # Get stream of toUnicode
            cmap_stream = page_font[1]['toUnicode']['Stream']

            # Get the raw mapping
            matches = pattern.findall(cmap_stream)
            if len(matches) > 1:
                print("error")
                break

            matches = matches[0].split("\n")
            mapping = {}
            for match in matches:
                item = match.split(" ")
                mapping[bytes.fromhex(item[0][1:-1]).decode('latin-1')] = chr(int(item[1][1:-1], 16))

            fonts_mapping[page_font[0]] = mapping

        return fonts_mapping

    def parse_text_elements(self, text_contents):
        """
            Parse text elmentents previously obtained from a content stream in a page.

            :param text_elements_content_stream: BT...ET text elements from content stream
            :return: return dict where every text element is mapped to its position
                    on the page.
        """
        # Extract font info such as /TT0 1 Tf and /F0 8.17 Tf
        patternTf = re.compile(r'/(TT\d|F\d+) ([+-]?\d*\.?\d+) Tf')

        """
            Extract text:
            1) Tm<00300030003000300031>Tj | <0036>Tj
            2) ()Tj | (\r\n)Tj | ( ) Tj | [(T)0.8(E)1.8(R)8.2( )0.7(B)6.8(E)-16.8(S)10.3(L)11.4(U)1.2(I)-5.6(T)0.8(V)8.8(O)2.1(R)-10.3(M)7.6(I)-5.6(N)-0.8(G )] TJ | [(B)5 (r)-0.7 (i)-7 (e)-5 (f)4.3 ( v)4.3 (ast)-7 (e)-5 ( co)-7.4 (m)-1.3 (m)-1.3 (i)-7 (ssi)-7 (e)-5 ( F)0.6 (i)-7 (n)-8 (.)3 ( )13.7 (aan)-8 ( )]TJ
            3) (\\000$\\000D\\000Q)Tj
        """
        patternText = re.compile(r'\[.*?\].*TJ|<.*?>.*Tj|\(.*?\).*Tj')
        patternTm = re.compile(r'\d+(\.\d+)?\s+-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s+\d+(\.\d+)?\s+-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s+Tm')
        test = re.compile(r'Tj|TJ')
        # Get every index (text_element)
        for i in range(len(text_contents)):
            #print(text_contents[i])

            # Get font reference
            #font_ref = patternTf.findall(text_contents[i])

            # Get text render
            text_ref = patternText.findall(text_contents[i])
            test2 = test.findall(text_contents[i])

            if len(text_ref) != len(test2):
                #TODO: only these cases need to be handled...
                print("OKEEE",text_contents[i], "\n-")
            #print(text_contents[i])

            #print(text_contents[i])

            #print(i, text_ref, end="\n\n")
            #for j in text_contents[i]:

            """if str(j).endswith("Tm"):
                    if len(str(j).split(" ")) > 7:
                        x = j.split(" ")[8]
                        y = j.split(" ")[9]
                        #print(x, y)
                    elif len(str(j).split(" ")) == 7:
                        x = j.split(" ")[4]
                        y = j.split(" ")[5]
                        #print(x, y)"""

        return None

        """text_elements = {}
        pattern = re.compile(r'(\(.*?\))(\w+)')
        for match in text_contents.items():
            font_info = {'reference': '/F0', 'fontsize': '11', 'match': ""}
            raw_string = ""
            split = match[1].strip().split("\n")
            for item in split:
                tokenized = ""
                if item[0] == "(":
                    tokenized = [item]
                else:
                    tokenized = item.split(" ")

                if tokenized[-1] == 'Tf':
                    font_info['reference'] = tokenized[0]
                    font_info['fontsize'] = tokenized[1]
                    font_info['match'] = item
                    continue
                elif tokenized[-1] == 'Tm':
                    x = float(tokenized[4])
                    y = float(tokenized[5])
                    raw_string = item
                elif len(tokenized) == 1:
                    try:
                        pk = codecs.escape_decode(tokenized[0].strip())[0].decode('utf-8', errors='replace').replace('\\)', ')')
                        # what if (..')'.'('...) ?
                        pk = pattern.match(pk)
                        # decode string here

                        # check if pk[1] == 'Tj'
                        text = pk.group(1)[1:-1]
                        raw_string = raw_string + "\n" + item
                        text_elements[(x, y)] = {'font': font_info, 'string': text, 'match': raw_string, 'index': match[0]}
                    except ValueError:
                        pass

        return text_elements"""

    def translate_text_elements(self, text_elements, fonts_mapping):
        """
            Translate text elements of a content stream of a page using the
            fonts character mapping from the page.
        """
        string = ""
        for text in text_elements.values():
            font_reference = text['font']['reference']
            value = text['string']
            for item in value[1:]:
                # empty/space charachter
                if item == "\x00 ":
                    string = string + item
                try:
                    string = string + fonts_mapping[font_reference.split("/")[1]]["\x00" + item]
                except:
                    pass

        return string