# Week 2: Design, PDF manipulation and some writing

## Tasks

1. Design a method of redaction based on literature which tackles the problems
2. Work out the steps in the tool:
   - How to select text?
   - How to redact text?
   - What to replace the redacted text with? (and why? => semantic definition of redacted text?) Options?
   - How to check if text is referenced anywhere else?
   - Metadata options
3. Finish first concept of **Related work**
4. Play around with PDF using PyMuPDF!!

## Findings

### 13-11:

PyMuPDF redaction method does NOT update the cmap; old charachters which may no longer be present in the PDF are not removed!

NEW IDEA: focus on TrueType fonts (apple, microsoft fonts), that are also frequently used in Word, since that is the main text editor used by bureacrats in the Netherlands (according to Maarten Marx).

Handeling other font types, especially font types which have cmaps is very difficult to handle right now. Requires a lot of work.

UPDATE: seems to be working with truetype fonts (calibri) where mapping (widths) of charachters are removed if not used.

Issues related to inserted text positioning which need to be handled.

## Literature

## Possible solutions
