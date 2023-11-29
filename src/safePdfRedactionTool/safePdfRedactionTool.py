from documentInterpreter import *
from documentReader import *
from documentManipulator import DocumentManipulator
import fitz

def printDict(dict, index=None):
    for i in dict:
        if index and len(index) > 0:
            for j in index:
                if j in dict[i]:
                    print(i, j, dict[i][j])
                    print()
                else:
                    print(j, "not in", i)
        else:
            print(i, dict[i])
            print()

def readFiles():
    reader0 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/pal.pdf")
    reader1 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/sns.pdf")
    reader2 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/marx.pdf")
    reader3 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/nota.pdf")
    reader4 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/appbeleid.pdf")
    reader5 = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/moties.pdf")

    readers = [reader0, reader1, reader2, reader3, reader4, reader5]

    # Get all roots
    roots = {}
    for i in range(len(readers)):
        root = {}
        root_xref = readers[i].doc.pdf_catalog()
        for key in readers[i].doc.xref_get_keys(root_xref):
            root[key] = readers[i].doc.xref_get_key(root_xref, key)

        roots[i] = root

    #print("Root of all documents:")
    #printDict(roots, ["Metadata"])

    # Get metadata
    #for i in range(len(readers)):
    #    print(readers[i].doc.metadata)

    """trailers = {}
    # trailer
    for i in range(len(readers)):
        trailer = {}
        trailer_xref = -1
        for key in readers[i].doc.xref_get_keys(trailer_xref):
            trailer[key] = readers[i].doc.xref_get_key(trailer_xref, key)

        trailers[i] = trailer

    print(trailers)

    # Get all metadata
    documentsMetadata = {}
    for i in range(len(readers)):
        metadata = {}
        if "Metadata" in
        metadata_xref = readers[i].get_object_num(trailers[i]['Metadata'])
        for key in readers[i].doc.xref_get_keys(metadata_xref):
            metadata[key] = readers[i].doc.xref_get_key(metadata_xref, key)

        documentsMetadata[i] = metadata

    print(documentsMetadata)"""

    # Get all 'Pages' object
    pagesObjects = {}
    for i in range(len(readers)):
        pageObj = readers[i].get_pages_object(roots[i]['Pages'])
        pagesObjects[i] = pageObj

    #print("Pages Object of all documents:")
    #printDict(pagesObjects)

    # Get all page objects of each document
    documentsPages = {}
    for i in range(len(readers)):
        page = readers[i].get_pages(pagesObjects[i]['Kids'])
        documentsPages[i] = page

    # TODO: resources -> xref, dict
    #print("Page objects of all documents:")
    #printDict(documentsPages)

    # Get all contents
    documentPagesContents = {}
    for i in range(len(readers)):
        # get all kids
        cont = {}
        for j in range(len(documentsPages[i])):
            content = readers[i].get_page_content(list(documentsPages[i].items())[j][1])

            # print here the pages content

            #print(i, content)
            #print("\n")
            cont[j] = content

        documentPagesContents[i] = cont

    #print(documentPagesContents)

    # Get all resources (images and fonts)
    documentPagesResources = {}
    for i in range(len(readers)):

        # get page
        resour = {}
        for j in range(len(documentsPages[i])):
            resource = readers[i].get_page_resources(list(documentsPages[i].items())[j][1])

            # print here the pages resources
            #print(i, j, resource, "\n")

            resour[j] = resource

        documentPagesResources[i] = resour

    #print(documentPagesResources)

    # Get all font info for all pages for all documents

    #print(">>> FONTS\n")
    documentPagesFonts = {}

    for i in range(len(readers)):
        fontTemp = {}
        for j in range(len(documentPagesResources[i])):
            font = readers[i].get_page_fonts(list(documentPagesResources[i].items())[j][1])
            #print(i, j,  font, "\n")
            fontTemp[j] = font

        documentPagesFonts[i] = fontTemp

    #print(documentPagesFonts)

    all_redactions = (b"226.935", b"721.212")

    return (readers, documentsPages, documentPagesFonts, documentPagesContents)


def main():
    """
    Example

    steps:
        for each page:
            read annotations/boxes/selected text
            retrieve text in boxes
            get cords/bounding box of text
            remove annots

            get lines of page
            get word of page

            add redact annots to page
            apply redactions

            get lines of page
            get word of page

            determine what to insert
            insert new text
            add white space before and after

            get lines of page
            get word of page

            remove white spaces
    """
    reader = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/test1.pdf")
    pages = reader.get_pages()
    for page in pages:
        dim = reader.get_page_dimensions(page)
        (xref, lines, words) = reader.get_page_contents(page)
        #print(words)

        to_be_redacted = words[3]
        test_rect = fitz.Rect(to_be_redacted[0], to_be_redacted[1], to_be_redacted[2], to_be_redacted[3])

        page.add_redact_annot(test_rect.quad)
        reader.doc.save("pdf_doc1_remove_text_test_temp.pdf")
        page._apply_redactions()

        (xref, lines, words) = reader.get_page_contents(page)
        #print(words)
        #print(words)

        to_be_repositioned = reader.get_to_be_repositioned_words(dim[1], lines, test_rect)
        print(to_be_repositioned)

        length = 0.0
        count = 0

        for i in range(len(to_be_repositioned)):
            string_line = to_be_repositioned[i][0].split()
            x = float(string_line[4]) if len(string_line) > 4 else float(string_line[0])
            y = dim[1] - float(string_line[5]) if len(string_line) > 3 else float(string_line[1])
            if count >= 1:
                length += float(to_be_repositioned[i - 1][0].split()[4]) - x
                new_pos = to_be_redacted[0] - length
            else:
                new_pos = to_be_redacted[0]

            if len(string_line) > 3:
                string_line[4] = str(new_pos).encode()
            else:
                string_line[0] = str(new_pos).encode()

            print(new_pos, string_line)
            new_string = b" ".join(string_line)
            #print(to_be_repositioned[i], new_string)
            lines[to_be_repositioned[i][1]] = new_string


            # removes all text after the
            #for k in range(i, i+2):
            #    lines[k] = lines[k]
            count += 1

        #print(lines)
        reader.doc.update_stream(xref, b"\n".join(lines))
        (xref, lines, words) = reader.get_page_contents(page)
        #print(lines)

    reader.doc.save("pdf_doc1_remove_text_test.pdf")
    reader.doc.close()
    """
    (readers, pages, fonts, contents) = readFiles()
    interpreters: List[DocumentManipulator] = []

    # Make interpreters based on readers
    for i in range(len(readers)):
        interpreters.append(DocumentInterpreter(readers[i].doc, pages[i], fonts[i], contents[i]))

    # Loop over interpreters and get text_elements

    # Get document
    for i in range(len(interpreters)):

        # Get contents object of document
        for j in interpreters[i].contents:

            # Get each content object of all contents object of document
            for k in interpreters[i].contents[j]:
                content_obj = interpreters[i].contents[j][k]
                stream = content_obj["Stream"]
                text_content = readers[i].get_text_content_from_stream(content_obj)
                #print(i, j, k, content_obj, "\n")
                #print(i, j, k, stream, "\n")
                #print(i, j, k, text_content, "\n")

                parsed = interpreters[i].parse_text_elements(text_content)
                #print(i,j,k,parsed, "\n")


                # TODO: parse text_content

                1) Tm<00300030003000300031>Tj | <0036>Tj
                2) ()Tj | (\r\n)Tj | ( ) Tj | [(T)0.8(E)1.8(R)8.2( )0.7(B)6.8(E)-16.8(S)10.3(L)11.4(U)1.2(I)-5.6(T)0.8(V)8.8(O)2.1(R)-10.3(M)7.6(I)-5.6(N)-0.8(G )] TJ | [(B)5 (r)-0.7 (i)-7 (e)-5 (f)4.3 ( v)4.3 (ast)-7 (e)-5 ( co)-7.4 (m)-1.3 (m)-1.3 (i)-7 (ssi)-7 (e)-5 ( F)0.6 (i)-7 (n)-8 (.)3 ( )13.7 (aan)-8 ( )]TJ
                3) (\\000$\\000D\\000Q)Tj




    """
    """
    # Rawreader = DocumentReader("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/testpdf/pal.pdf")
    root = reader.get_root_object()
    pagesObj = reader.get_pages_object(root['Pages'])
    pagesDoc = reader.get_pages(pagesObj['Kids']) fonts and contens
    fonts = {}
    contents = {}

    for page_xref in pagesDoc:
        #fonts[page_xref] = reader.get_page_fonts(pagesDoc[page_xref])
        page_content = reader.get_page_content(pagesDoc[page_xref])
        temp_content = {}
        for cnt in page_content.items():
            temp_content[cnt[0]] = cnt[1]
        contents[page_xref] = temp_content


    interpreter = DocumentInterpreter(reader.doc, pagesDoc, fonts, contents)

    # Font mappings, text_contents, text_elements
    cmaps = {}
    text_contents = {}
    text_elements = {}

    for page_xref in pagesDoc:
        # Do something with more then 2 per entry/mapping
        #cmap = interpreter.parse_character_mapping(interpreter.fonts[page_xref])
        temp_text_elements = {}
        temp_text_contents = {}
        for content_xref in contents[page_xref]:
            text_content = reader.get_content_from_stream(contents[page_xref][content_xref])
            temp_text_elements[content_xref] = interpreter.parse_text_elements(text_content)
            temp_text_contents[content_xref] = text_content

        #cmaps[page_xref] = cmap
        text_contents[page_xref] = temp_text_contents
        text_elements[page_xref] = temp_text_elements

    #print(text_contents)
    #print(text_elements)

    #test_text_element = text_elements[6][17][(226.935, 721.212)]

    # end of text character...
    #test_text_element2 = text_elements[6][17][(274.263, 721.212)]

    for item in text_elements[6][17].items():
        if item[0][1] == 721.212 and item[0][0] >= 226.935:
            print(item)

    manipulator = DocumentManipulator(reader.doc, text_contents, contents, text_elements)
    print(manipulator.text_elements.items())
    manipulator.remove_text(6, 17, 0, ((226.935, 721.212), test_text_element))
    manipulator.remove_text(6, 17, 0, ((274.263, 721.212), test_text_element2))
    manipulator.remove_white_space(6, 17, 0, ((226.935, 721.212), test_text_element))
    manipulator.finalize_manipulation()
    manipulator.save_document()

    # text_translated = interpreter.translate_text_elements(text_elements, cmap)
    """

# Using the special variable
# __name__
if __name__=="__main__":
    main()