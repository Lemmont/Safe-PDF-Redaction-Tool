from .DocumentRedactor import DocumentRedactor
from .RedactionSelector import RedactionSelector
from .LineInterpreter import LineManipulator

def redact_file(file, num=1, input=[], mode="replace", display=False, metadata=False, save_steps=True, pos_adj_changed=False):
    prefix = str(file).split("/")[-1].split(".")[0]
    """
    Redact a file based on specified parameters.

    Parameters:
    - file: File path of the document to be redacted.
    - num: Number of redactions to generate.
    - input: Optional input for redaction selection.
    - mode: Redaction mode ("replace" or "white").
    - display: display information about document and redaction (False or True)

    Returns:
    - redactions: Dictionary containing generated redactions.
    """
    # Initialize DocumentRedactor and RedactionSelector
    redactor = DocumentRedactor(file)
    redaction_selector = RedactionSelector(redactor)

    # Select redactions based on input or generate them
    redactions = redaction_selector.select_redactions(num, input)
    # Save the document with added redactions
    redactor.add_redactions(redactions)

    if save_steps:
        redactor.doc.save(prefix + "-indicated.pdf")

    # Apply redactions based on the specified mode
    if mode == "replace":
        redactor.apply_redactions_with_replacements()
    elif mode == "white":
        redactor.apply_redactions_without_replacements()
    else:
        print("Error: Invalid mode")
        return

    # Save the document after applying redactions

    if save_steps:
        redactor.doc.save(prefix + "-removed.pdf")

    # Edit positional information
    has_been_changed = redactor.edit_positional_information()

    if metadata:
        redactor.redact_metadata(redactions, inputs=input)
        redactor.redact_xml_metadata(redactions, inputs=input)

    # Remove attached_files, comments, embedded_files, hidden_text, javascript, links, responses, thumbnails and rest form fields.
    redactor.doc.scrub(metadata=False, xml_metadata=False)
    # Save the document after editing positional information
    redactor.doc.save(prefix + "-redacted.pdf", garbage=4, clean=True)

    # Display information if true
    if display:
        print(redactor)
        print(redaction_selector)

    if pos_adj_changed:
        f = open("res.txt", "a")
        temp = False
        for page in redactions:
            if len(redactions[page]) > 0:
                temp = True
        if temp:
            print(prefix, ": pos. adj. have been changed?", has_been_changed)
            f.write(prefix + " " + has_been_changed)
        else:
            print(prefix, ": no redactions or redactions found, no pos. adj. changed")
            f.write(prefix + " " + "None")
        f.close()

    return redactions


