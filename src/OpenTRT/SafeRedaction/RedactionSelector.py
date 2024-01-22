from typing import List, Dict
from SafeRedaction import DocumentRedactor
import random
import fitz

class RedactionSelector:
    def __init__(self, document_redactor):
        """
        Initialize the RedactionSelector.

        Parameters:
        - document_redactor: An instance of DocumentRedactor.DocumentRedactor.
        """
        self.redactor: DocumentRedactor.DocumentRedactor = document_redactor
        self.redactions: Dict = None

    def __str__(self) -> str:
        """
        String representation of the RedactionSelector object.

        Returns:
        - str: A string containing information about generated redactions per page.
        """
        msg = "--- GENERATED REDACTIONS PER PAGE ----\n\n"

        # Check if redactions exist
        if self.redactions is not None and self.redactions != {}:
            for i in self.redactions:
                msg += str(i) + "\n--- REDACTIONS ----\n"
                for j in self.redactions[i]:
                    msg += "> " + str(j) + "\n"
                msg += "\n"
        else:
            msg = "no redactions"

        return msg

    def select_redactions(self, num=1, input=[]):
        """
        Select or generate redactions for the document.

        Parameters:
        - num: Number of redactions to generate.
        - input: Optional input for redaction selection.

        Returns:
        - Dict: A dictionary containing redactions per page.
        """
        pages = self.redactor.pages
        redactions = {}

        # Check if specific input is provided for redaction selection
        if input != []:
            redactions = _select_redaction_based_on_input(pages, input[0])
        else:
            # Generate redactions per page
            redactions = _generate_redactions_per_page(self.redactor, pages, num)

        self.redactions = redactions
        return redactions


def _select_redaction_based_on_input(pages: List[fitz.Page], input):
    """
    Select words based on a specified input on each page.

    Parameters:
    - pages: List of fitz.Page objects representing pages in the document.
    - input: The specified input for searching.

    Returns:
    - words_selected: Dictionary where keys are pages and values are lists of selected words.
    """
    words_selected = {}

    # Iterate through each page
    for page in pages:
        selected = []
        res = page.search_for(input)

        # Iterate through each search result on the page
        for r in res:
            # Get the text elements (words) within the specified clip (search result)
            text = page.get_text("words", clip=r, sort=True)

            # Append the selected words to the list
            for t in text:
                selected.append(t)

        # Store the selected words for the current page in the dictionary
        words_selected[page] = selected

    return words_selected


def _select_multiple_redactions_example(words, num):
    """
    Randomly select a specified number of words from a list.

    Parameters:
    - words: List of words to select from.
    - num: Number of words to randomly select.

    Returns:
    - words_list: List of randomly selected words.
    """
    words_list = []
    b = []

    # Continue selecting random words until the specified number is reached
    while len(b) != num:
        for i in range(random.randint(1, num)):
            a = random.randint(0, len(words) - 1)

            # Check if the selected word index is not already in the list
            if a not in b:
                b.append(a)

            # Break if the specified number of words is reached
            if len(b) == num:
                break

    # Sort the selected indices
    b.sort()

    # Retrieve the selected words based on the indices
    for j in b:
        words_list.append(words[j])

    return words_list

def _generate_redactions_per_page(redactor: DocumentRedactor, pages, num):
    """
    Generate redactions for each page by randomly selecting a specified number of words.

    Parameters:
    - redactor: An instance of DocumentRedactor.
    - pages: List of fitz.Page objects representing pages in the document.
    - num: Number of words to randomly select for redactions on each page.

    Returns:
    - redactions_per_page: Dictionary where keys are pages and values are lists of generated redactions.
    """
    redactions_per_page = {}

    # Iterate through each page
    for page in pages:
        # Clean the contents of the page
        page.clean_contents()

        # Get the text (words) on the page
        words = page.get_text("words", sort=True)

        if len(words) == 0:
            redactions_per_page[page] = {}
            continue

        # Select a specified number of words for redactions on the page
        redactions = _select_multiple_redactions_example(words, num)

        # Store the generated redactions for the current page in the dictionary
        redactions_per_page[page] = redactions

    return redactions_per_page
