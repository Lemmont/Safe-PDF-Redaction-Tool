from typing import Dict
import fitz
import re
class DocumentInterpreter:
    def __init__(self, document: fitz.Document, pages: Dict[int, fitz.Page], fonts: Dict[int, str]):
        self.doc: fitz.Document = document
        self.pages: Dict[int, fitz.Page] = pages # TO BE EDITED
        self.fonts: Dict[int, Dict[str, any]] = fonts # TO BE EDITED

    def parse_character_mappings(self, page_fonts: Dict[str, any]):
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