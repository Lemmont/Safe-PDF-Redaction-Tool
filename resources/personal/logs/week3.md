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

### 16-11:

Gland:

> *The glyph shifts present in a PDF document are dependent on the specific workflow used to produce the PDF document. This includes an originating software, called the PDF producer by the ISO 32000 PDF standard [19], and any software that may modify the PDF file contents thereafter,
including, for example, a redaction tool. A given workflow creates a specific pattern of glyph shifts,
determining, in part, the security of any redacted text* (p. 4)

Microsoft Word "Save as a PDF" have a class of dependent schemes. Word Desktop 2007 to 2016 use a different scheme then Word desktop 2019 to present.

### 15-11:

Worked a lot on trying things with PDF.

Design idea:

1. Text selection method (drawing bounding boxes?)
   - Also give suggestion on where all instances of a text value are located.
2. Redaction method
3. Semantic filling?
4. Metadata deletion and custom additions

Most important is the redaction method!! Some ideas:

- Remove text
- Update cmaps of font -> difficult, but most likely necessary. Have to iterate whole PDF range of characters and re-create a whole new mapping so that we can leave out mappings that are not used and thus leave out possible vunerable leaks.
- Do not leave the width of the original text. Actually remove the text and either fill it with a fixed sized text or none at all.
- Check for version control or other history related information?

Redacted text may be filled in with text which maintains the semantic definition of the text.

- Check original text and what kind of semantic value/definition it represents.
- Determine a replacement value

### 13-11:

PyMuPDF redaction method does NOT update the cmap; old charachters which may no longer be present in the PDF are not removed!

NEW IDEA: focus on TrueType fonts (apple, microsoft fonts), that are also frequently used in Word, since that is the main text editor used by bureacrats in the Netherlands (according to Maarten Marx).

Handeling other font types, especially font types which have cmaps is very difficult to handle right now. Requires a lot of work.

UPDATE: seems to be working with truetype fonts (calibri) where mapping (widths) of charachters are removed if not used.

Issues related to inserted text positioning which need to be handled.

## Literature

## Possible solutions
