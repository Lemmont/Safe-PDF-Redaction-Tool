import re
import fitz
import random
from typing import List
import xml.etree.ElementTree as ET

from .DocumentRedactor import DocumentRedactor
from .RedactionSelector import RedactionSelector
from .LineInterpreter import LineManipulator

def redact_file(file, num=1, input=[]):
    #file.split("/")[-1] +
    redactor = DocumentRedactor(file)
    redaction_selector = RedactionSelector(redactor)
    redactions = redaction_selector.select_redactions(num)
    print(redaction_selector)
    redactor.add_redactions(redactions)
    redactor.doc.save("temp.pdf")
    redactor.apply_redactions_with_replacements()
    redactor.doc.save("temp2.pdf")
    redactor.edit_positional_information()
    redactor.doc.save("temp3.pdf")


