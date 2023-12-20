from .DocumentRedactor import DocumentRedactor
from .RedactionSelector import RedactionSelector
from .LineInterpreter import LineManipulator

def redact_file(file, num=1, input=[], mode="replace", display=False, metadata=False):
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

    #redactor.doc.save("temp.pdf")

    # Apply redactions based on the specified mode
    if mode == "replace":
        redactor.apply_redactions_with_replacements()
    elif mode == "white":
        redactor.apply_redactions_without_replacements()
    else:
        print("Error: Invalid mode")
        return

    # Save the document after applying redactions

    #redactor.doc.save("temp2.pdf")

    # Edit positional information
    redactor.edit_positional_information()

    if metadata:
        redactor.redact_metadata(redactions, inputs=input)
        redactor.redact_xml_metadata(redactions, inputs=input)

    # Save the document after editing positional information
    redactor.doc.save("temp.pdf")

    # Display information if true
    if display:
        print(redactor)
        print(redaction_selector)

    return redactions


