from typing import Tuple, List

class RootObject():
    def __init__(self, xref:int, pages: Tuple[str, str], metadata: Tuple[str, str]):
        self.xref = xref
        self.pages: Tuple[str, str] = pages
        self.metadata: Tuple[str, str] = metadata

class PagesObject():
    def __init__(self, xref: int, kids: List[int], count:int):
        self.xref = xref
        self.kids = kids
        self.count = count

class PageObject():
    def __init__(self, xref: int, contents, mediabox, resources):
        self.xref = xref,
        self.contents = contents,
        self.mediabox = mediabox,
        self.resources = resources
