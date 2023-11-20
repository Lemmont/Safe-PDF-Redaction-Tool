import fitz
from typing import List

class DocumentReader:
    """
        A class that reads the internals of a PDF document

        add more info
    """
    def __init__(self, document):
        self.doc: fitz.Document = fitz.open(document, filetype="pdf")

    def get_object_num(self, xref) -> int:
        """
            Extract the object number that is referenced by a object.

            :param xref: xref object.
            :return: integer value of object that is referenced.
        """
        temp = xref[1].strip('[]').split()
        temp = [item.strip(",") for item in temp]
        return int(temp[0])


    def get_object_array_num(self, array: List[str]) -> List[int]:
        """
            Extract object numbers from a array that is referenced by an object.

            :param array: array with reference(s) to object(s) in string format.
            :retun: list of object references in integer.
        """
        temp = array.strip('[]').split()
        temp = [item.strip(",") for item in temp]
        pdf_pages_xref = temp[::3]
        pdf_pages_xref = [int(x) for x in pdf_pages_xref]
        return pdf_pages_xref

    def get_object_dictionary(self, xref, check_stream) -> dict:
        """
            Extract the dictionary of the object

            :param xref: object being referenced.
            :param check_stream: check if presence of a stream should be checked.
            :return: dictionary of key-value pairs.
        """
        temp_dict = {}

        for key in self.doc.xref_get_keys(xref):
            temp_dict[key] = self.doc.xref_get_key(xref, key)
        if check_stream and (stream := self.doc.xref_stream(xref)):
            temp_dict["Stream"] = stream.decode("latin-1")

        return temp_dict

    def get_root_object(self):
        """
            Get 'Root' object of document.

            The start point of every PDF document is read here for further
            processing.

            :return: dictionary with Root object information
        """
        root_xref = self.doc.pdf_catalog()
        return self.get_object_dictionary(root_xref, check_stream=False)

    def get_pages_object(self, pages_xref):
        """
            Get 'Pages' object of document.

            param: pages_xref: reference to 'Pages' object.
            :return: dictionary with Pages object information
        """
        return self.get_object_dictionary(self.get_object_num(pages_xref), check_stream=False)

    def get_pages(self, kids_xref):
        """
            Get the actual pages of the document

            :param kids_xref: reference to the kids of the pages object.
            :return: one or more 'Page' objects in a dictionary. {xref: page_info, ...}
        """
        pages_xref = []
        pdf_pages = {}

        # Get reference numbers from xref object
        if kids_xref[0] == 'array':
            pages_xref = self.get_object_array_num(kids_xref[1])
        else:
            pages_xref = self.get_object_num(kids_xref[1])

        # Get information for every page in list.
        for xref in pages_xref:
            pdf_pages[xref] = self.get_object_dictionary(xref, check_stream=False)

        return pdf_pages

    def get_page_content(self, page):
        """
            Extract the contents for a given page.

            :param page: page information/dictionary
            :return: page content
        """
        page_contents = {}
        contents_xref = []
        contents = page['Contents']

        # Get all referejces to 'Contents' object(s) from this page.
        if contents[0] == 'array':
            contents_xref = self.get_object_array_num(contents[1])

        # Get all 'Contents' objects information.
        for content_xref in contents_xref:
            page_contents[content_xref] = self.get_object_dictionary(content_xref, check_stream=True)

        return page_contents

    def get_content_from_stream(self, page_content):
        """
            Extract text elements from a content stream of a page.

            :param page_content: content of a page
        """
        import re
        import codecs
        content_stream = page_content['Stream']

        # Get all text elements (BT...ET) from content stream
        return re.findall(r'BT(.*?)ET',content_stream, re.DOTALL)

    def get_page_resources(self, page):
        """
            Extract information about the resources referenced by the page
        """
        resources = page['Resources']

        if resources[0] == 'xref':
            resource_xref = self.get_object_num(resources)

        return self.get_object_dictionary(resource_xref, check_stream=False)

    def get_page_fonts(self, page):
        """
            Extract fonts used by page

            :param page: page information/dictionary
            :return: information of the font used by page
        """
        fonts_xrefs = {}

        fonts = self.get_page_resources(page)['Font']

        # Get all font references for this page.
        if fonts[0] == 'dict':
            # example: <</F3 19 0 R/F2 20 0 R/F1 21 0 R/F0 22 0 R>>
            fonts_ref = fonts[1].strip("<<>>").split("/")[1:]
            for font_ref in fonts_ref:
                tokens = font_ref.split(" ")
                fonts_xrefs[tokens[0]] = int(tokens[1])
        else:
            print("error")

        fonts_info = {}

        # Get information for every font reference.
        for font_xref in fonts_xrefs.items():
            fonts_info[font_xref[0]] = self.get_object_dictionary(font_xref[1], check_stream=False)

        fonts = {}

        # Get character mapping and descendent fonts
        for font in fonts_info.items():
            toUnicode = {}
            descendant = {}
            toUnicode_xref = font[1]['ToUnicode']
            descendent_xref = font[1]['DescendantFonts']

            if toUnicode_xref[0] == 'xref':
                toUnicode_xref = self.get_object_num(toUnicode_xref)
                toUnicode = self.get_object_dictionary(toUnicode_xref, check_stream=True)

            if descendent_xref[0] == 'array':
                descendent_xref = self.get_object_array_num(descendent_xref[1])[0]
                descendant = self.get_object_dictionary(descendent_xref, check_stream=True)

            fonts[font[0]] = {'toUnicode': toUnicode, 'descendentFonts': descendant}

        return fonts
