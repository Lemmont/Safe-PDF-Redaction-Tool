import fitz

class Reader:
    def __init__(self, file):
        self.file: fitz.Document  = fitz.open(file, filetype="pdf")

    def get_pages(self):
        return self.file.pages()

reader1 = Reader("../resources/testpdf/marx.pdf")
pages = reader1.get_pages()
for page in pages:
    print(page)