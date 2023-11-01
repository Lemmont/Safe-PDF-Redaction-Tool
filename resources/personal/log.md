# Logbook

### 3 Nov

- Laatste check projectplan
- Projectplan inleveren
- ...

### 2 Nov

- Ochtend: stuur projectplan naar Maarten
- PDF specifications bekijken 2
- Feedback verwerken
- Nogmaals opsturen indien nodig?
- ...

### 1 Nov

#### New literature found:

https://arxiv.org/abs/2005.11687

https://dl.acm.org/doi/abs/10.1145/3011141.3011217?casa_token=ZCptE4ZjDIcAAAAA:PpXSTSJLQctThzFji1x39w7aZDXo2H3xC-Sq2uM5PEQLueT4u-QRu4EdknJaXMAQakytOECB1YM

https://dl.acm.org/doi/abs/10.1145/3558100.3563849?casa_token=eE5CQzUuBIYAAAAA:bCj423iY3fsr-uF8fMCSkwQG_NNJy6HCVZkNfQ_GQcgG47JrjvG0Zvf8DR7lZf_b7Fv8Rvfnd2M

- Time schedeling + course of action coming weeks
- Write out projectplan v1
- Literature search + read
- Review projectplan
- Write out projectplan v2
- Literature search + read
- Final projectplan check

### 31 Oct

- Think about the problem. Compile it based on findings.

> Safe and reliable text redaction that does:

    1. not just cover text with a black box
    2. not leave relevant information in metadata (or any other part of the document)
    3. not preserve the length of the redacted text, especially in cases where the redacted text represents a name, date, organisation or any other PII.
    4. not change or damage non-redacted text
    5. keep in mind the glyph shifts and widths.
    6. find a relevant replacement for the redacted text?

- Think about the possible solutions based on my findings.

  1.  Remove text, replace it with a relevant replacement text (standarize width, font etc.)
  2.  Remove metadata references
  3.  Remove information about glyph shifts: either change PDF font and shifts for non-redacted glyphs or remove them altogheter.
  4.  Do not preserver original length, but make every redaction of PII of same length (or set of lengths)

- Think about what I think I can achieve and how.

  1.  Create a super secure text redaction standard/method which prioritizes safety above maintaining.
  2.  Python (Pymupdf), Web based application?
  3.  Way to check/text my own method (X-ray etc.)

- Formulate a research question

  _How can we design and develop a PDF text redaction tool (/method?) that effectively addresses security concerns, including the prevention of information leakage through glyph shifts and width equivalence classes, while preserving non-redacted text._

- Formulate possible solution(s) for this questions
- Think about the methods.

  - Literture study: security concerns, security issues, possible solutions to these problems and relevant tool/research on checking and validating redaction safety/quality.
  - Learn about the PDF extensions and the internals. Get to know the relevant and 'state-of-the-art' python libraries etc.
  - Design my method based on findings
  - Start creating and implementing my method. Make if useable
  - Collect/create test documents for redaction and use them with my program. Test them using found 'safety checkers' and possible techniques produced by my me.
  - Do something based on my findings.

- Think about the course of action.

  (1) (mediocre)

  - Literature study and PDF internals
  - Practical implementation and testing of py libraries etc. and the manipuation of pdf files with these libraries and other means.
  - Write Thesis Part: context, safety concerns, problems, relevant literature etc.

  (2) (a lot of time)

  - Design my own method based on findings
  - Practical implementaion and testing

  (3) (a lot of time)

  - Practical implementation of design
  - Testing While Implementing (TWI)

  (4) (few)

  - Getting example documents
  - Using example documents
  - Checking safety of documents.

  (5) (few)

  - Finalizing

- Think about time schedeling
  ~ 10 weeks

Search for relevant literature when needed.

[Generation of Replacement Options in Text Sanitization](https://aclanthology.org/2023.nodalida-1.30.pdf) (2023) (cited by 2) -> veel related work

#### Some on automatic redaction/de-identification

[Automatic de-identification of textual documents in the electronic health record: a review of recent research](https://pubmed.ncbi.nlm.nih.gov/20678228/)

[C-sanitized: A privacy model for document redaction and sanitization](https://asistdl.onlinelibrary.wiley.com/doi/abs/10.1002/asi.23363) (cited by 87)

[De-identification of patient notes with recurrent neural networks](https://academic.oup.com/jamia/article-abstract/24/3/596/2769353?redirectedFrom=fulltext)

#### Case study

[Anonymisation Models for Text Data: State of the Art, Challenges and Future Directions](https://aclanthology.org/2021.acl-long.323.pdf) (2021) (cited by 45)

### 30 Oct

- Search for relevant literature and read it. Does it add to my project's research question or not? What kind of value does it add and is it relevant?

Relevant literature that I found up till this point:

1. [PDF redaction is broken by Glyph Positions](https://arxiv.org/abs/2206.02285v3)

- adad

2. [Forrester and Irwin discuss trivial redactions and unscrubbed metadata such as the Producer field of PDF documents but do not mention glyph positioning based deredaction](https://www.researchgate.net/publication/229014289_An_Investigation_into_Unintentional_Information_Leakage_through_Electronic_Publication): 5 citations.

   - Advanced features; such as group editing, version control and multi-user authoring; leave metadata that is used to enable the collaborative features.

   - > _Abstract: "This paper outlines the types of data that can be extracted from documents through the use of freely available tools. It has also outlined potential uses for this information from the point of view of a digital forensic investigator and for possible exploitation."_

   - Hidden data in advanced document editing applications: author's name for authoring documents effectively. Hidden data is crucial for offering an advanced editing application [Byers. S about Information Leakage Caused by Hidden Data in Published Documents](https://sci-hub.se/https://ieeexplore.ieee.org/abstract/document/1281241)

   - Same paper states that Byers discovered that in word documents retrieved from the internet, 50% had 10 to 50 hidden words, one third revealed between 50 and 500 words, and 10% had more thant 500 words.

   - What information can be found?

     1. Versions
     2. Track Changes (made to a document by the various authors that edit the document. Comments.),
     3. Metadata (about the author, the document and organisation): author's full name, manager name, company name, document keywords, template used, computer username, previous authors, printer details, date printed, created, modified, accessed, last saved by, revision numbers, revision comments, full path to the documents location.
     4. Fast saves?
     5. Password hashes.

   - How to view metadata? -> **PDF METHODS?**

   - What can data be used for?

     1. Coroporate espionage
     2. Identity Theft
     3. Selling of Data
     4. Discovery and reconnaissance (networks)

   - Relevant literature that I found new:

   [What you see is not what you get in the PDF document; What you see is what you store](https://journals.sagepub.com/doi/full/10.1177/1460458210397851#bibr3-1460458210397851) (2011)

   [Scanning electronice documents for personally identifiable information](https://dl.acm.org/doi/abs/10.1145/1179601.1179608) (2006)

   - _"A content stream in a PDF file is handled in a sequential manner, and therefore the images will be placed onto the page before the rectangle that masks the eyes on one of the images."_

   - _"The images on page 5 of the document are all defined as XObjects. This is because the images are of a certain nature and therefore will be treated as external objects to the file. XObjects are one of five possible types of graphical objects within a PDF file, the other four being path objects, text objects, inline images, and shading objects (8.2). The mask of one of the images on page 5 will be made into a path object and therefore is not a part of the XObject itself."_

3. [On security and Privacy of The PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_1B-2_23109_paper.pdf) (2021) (cited by 6)

   - also talks about PDF basics!

   - (page 11): hidden data in pdf documents:
   - Evitable Metadata
   - Revision recovery:
     - _"However, we determined potential security issues in Acrobat Pro and and four other PDF editors, whereby we deleted the content (text or image). The removed content is not displayed anymore, but it is still contained in the file and can be extracted."_
     - _"The PDF standard allows editing applications to modify existing documents while only appending to the file and leaving the original data intact. Whenever new content is added to the document, it is not simply inserted into the existing body section. Instead, a new body section is appended at the end of the PDF file containing new objects.30 This feature is called “incremental updates”. It enables authors, for example, to undo changes. However, it also enables third parties to restore previous versions of the document, which may not be desired in the context of privacy and document security. Especially when sensitive content is explicitly redacted/blackened in a document to be published, this can be dangerous"_
     - Different pdf applications and their security with metadata and revision recovery.

4. [An Examination of the
   Redaction Functionality of
   Adobe Acrobat Pro DC 2017](https://www.cyber.gov.au/sites/default/files/2023-03/PROTECT%20-%20An%20Examination%20of%20the%20Redaction%20Functionality%20of%20Adobe%20Acrobat%20Pro%20DC%202017%20%28October%202021%29.pdf)

   - _"If the PDF document was created with Adobe Acrobat, Adobe Acrobat Distiller or Microsoft Word, the PDF Producer field will contain ‘Adobe PDF Library’, ‘Acrobat Distiller’ or‘Microsoft Word’ respectively. If the PDF Producer field contains something else, there is a chance that redaction of sensitive or private information might fail. Note that if the PDF document had been previously sanitised, the metadata would have been deleted and the PDF Producer field will be empty. "_

5. [The National Security Agency’s redaction guide does not mention glyph positioning information but notes any underlying redacted text should be removed from the document before producing a PDF.](https://sgp.fas.org/othergov/dod/nsa-redact.pdf) (2005)

   - _"The most common mistake is covering text with black."_
   - _"Covering up parts of an image with separate graphics such as black rectangles, or making images ‘unreadable’ by reducing their size, has also been used for redaction of hardcopy printed materials."_
   - **_"The way to avoid exposure is to ensure that sensitive information is not just visually hidden or made illegible, but is actually removed from the original document."_ **

6. [Hill et al., used hidden Markov models to recover text obscured either by mosaic pixelization or a related tactic, e.g. Gaussian Blur](https://cseweb.ucsd.edu/~saul/papers/pets16-redact.pdf) (2016)

   - Redaction through _mosaicing/pixelation_ and _blurring_.
   - Simple but powerful class of statisitcal models can be used to recover both short and indefinitely long instances of redacted text.
   - Redaction through these methods are **not** viable options.
   - _"Both mosaicing and blurring are lossy, so they cannot, in general, be reversed to recover the original image. But if the original image has predictable regularities— as occur in text— then enough information may remain after filtering to recover the redacted text, or at least to narrow down its space of possibilities."_
   - _"While we have yet to witness a large-scale attack on redacted text, it is important to recognize the widespread potential for abuse. Simple online searches return scores of images for redacted names, phone numbers, email addresses, passwords, credit card numbers, personal checks, private conversations, and other sensitive information. Mosaicing and blurring have also been used for the redaction of high-profile government documents and celebrity social media. It is self-evident that an attacker could exploit such sensitive information for malicious purposes (e.g., identity theft, blackmail)."_

7. [The In/Visibilities of Code and the Aesthetics of Redaction](https://researchbank.swinburne.edu.au/file/c52fe75d-3c0c-4275-98be-62f7f2b8763c/1/PDF%20%28Published%20version%29.pdf) (2013) (cited by 1)

   - _"By drawing material attention to what is withheld, the absent text becomes a central focus of perception, a curious sort of visibility"_

8. [Quantifying Information Leakage in Document Redaction](https://www.cse.lehigh.edu/~lopresti/Publications/2004/hdp04a.pdf) (2004) (cited by 13)

9. [Toward an Extensible Framework for Redaction](https://seclab.illinois.edu/wp-content/uploads/2018/06/demetriou2018toward.pdf) (2018) (cited by 0) (2023) (cited by 0)

10. [Towards Quantifying the Privacy of Redacted Text](https://link.springer.com/chapter/10.1007/978-3-031-28238-6_32)

### 27 Oct '23

#### (11:00-13:30) Research on PDF file extension:

[Stackoverflow discussion on how to inspect the structure of PDF files](https://stackoverflow.com/questions/3549541/how-can-i-visually-inspect-the-structure-of-a-pdf-to-reverse-engineer-it)

[A high performance Python library for data extraction, analysis, conversion & manipulation of PDF (and other) documents.](https://pypi.org/project/PyMuPDF/)

[PDF 1.4 specifications](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.4.pdf)

#### (8:30-11:00) _Bland_EdactRay_2022.pdf_ notes:

Security of PDF document depends on the specification. A **raster image** of the original document or a document type that contains text data for both the font and the layout of each character (**glyph**) on the page.

Text is rendered in numerous ways. An example is by use of a **text showing operator**. It takes as arguments a **(1)string of text** and a **(2)vector of positional adjustments** which displace the charachter with respect to a default position, usually **a fixed offset from the previous character equivalent to the advance width of the previous character defined elsewhere in the PDF document**

Paper introduces a intermediate representation; **a set of advance widths and glyph shifts** which are the sum of all the individual positioning operations applied to a glyph.

Positional adjustments in _text space units_ between glyphs. These units express **glyph shifts** where 1000 units almost always equals the point size of the fint times 1/72 of an inch.

Glyph advance widths and glyph shifts create a security concern:

1. The precise width of the redaction can be used to eliminate potential redacted texts
2. Any non-redacted glyph shifts conditioned on redacted glyphs can be used to eliminate
   potential redacted texts

> The width of a PDF redaction depends on glyph shifts. Without accounting for glyph shifts, redacted text guesses are imprecise and must account for error, reducing the potential of finding a unique match for redacted content. _The width of a PDF redaction depends on glyph shifts. Without accounting for glyph shifts, redacted text guesses are imprecise and must account for error, reducing the potential of finding a unique match for redacted content_

##### Glyph Shifts

Glyph shifts in PDF document are dependent on the specific workflow from a _PDF producer_ by the ISO 32000 PDF standard, and any software that may modify the PDF.

**Independent glyph shifts** for a given character are not dependent on any other character, while **dependent glyph shifts** are dependent on some other charachter in the document in some way. These are called **glyph shifting schemes** that are created by a specific workflow. Independent schemes are _unadjusted_ when there are no shifts on any character.

_Equivalence Classes. Before discussing these schemes further, we introduce the idea of width and shift equivalence classes. A shift equivalence class is a set of lists of glyphs of the same length with identical shift values. A width equivalence class is a set of glyphs and associated shifts with the same width_

> The PDF specification does not include any specific signifiers for redacted text. However, residual specification information after redaction, such as glyph positions, can be used to reasonably rule out large numbers of candidate width and shift equivalence classes for redacted text. None of the prior words in this paragraph are in the width equivalence class of the word cat.

_In an independent glyph shifting scheme, the security of a redaction may be considered dependent on the size of the width equivalence class indiscated by the PDF document’s residual glyph positioning information. That is, the positions of glyphs prior to and succeeding the redaction may leak the width of redacted text. The scheme’s specific glyph shifts can make a given width equivalence class leak more or less redacted information by making width of individual glyphs more or less unique._

_Dependent Schemes.A dependent scheme is more dangerous to the security of redacted text than an independent scheme. In these schemes non-redacted glyph shifts can be dependent upon redacted glyph information, because the non-redacted glyph shifts can be determined before redaction_

##### Protecting Redactions

> _"Edact-Ray protects vulnerable PDF redactions by first locating the nonexcising redactions and removing their underlying text from the PDF. We then adopt a userconfigurable level of information excisement by allowing users to optionally remove all non-redacted glyph shifts13 and optionally convert the font to a monospaced one, scaling the size to preserve readability. To protect excising redactions, Edact-Ray can round up the size of all spaces between two words to some width, 𝑛 × 𝑤, where 𝑛 is some number of characters and 𝑤 is width of a single character in the monospace font. Edact-Ray can also remove any rectangular draw commands from the PDF so that the width of the redaction cannot be recovered by examining the width of any graphical box drawn to represent the redaction."_

(!) Monospace font?

##### Recommended practices

> Redaction practices must account for concerns about document integrity. All the above measures
> modify the redacted document beyond simply removing text. In some contexts, particularly due
> to legal or regulatory reasons, this may not be acceptable. One of the main reasons for releasing
> redacted documents is to demonstrate transparency while still protecting sensitive information.
> Altering parts of the document outside the redaction alters this promise of authenticity.

> It is technically possible to fix a non-excising redaction by removing the redacted text. The effect would be the same as if the document were redacted by an excising redaction tool. However, this also raises the issue of authenticity of done by a third party (e.g. document repository operator), because this necessarily means modifying the original document without the author’s involvement. In cases where integrity requirements may be relaxed, the NSA-recommended practice of altering the original document to replace the redacted text with meaningless text, e.g. REDACTED, provides the highest level of security.

> In cases where the underlying text may not be changed, we offer the following two suggestions.
> First, we note that redacting a name from a PDF is not secure. If a name occurs on a line of
> text, the entire line should be redacted, if possible, or care should be taken to ensure that enough of the surrounding words are redacted to make deredaction unlikely. Second, if redacting more text is not possible, the width of the redaction should be quantized to a fixed value, and any glyph shifts should be removed. While this may make the file less aesthetically pleasing, it is necessary for the security of redactions.

##### Related work

[Forrester and Irwin discuss trivial redactions and unscrubbed metadata such as the Producer field of PDF documents but do not mention glyph positioning based deredaction](https://www.researchgate.net/publication/229014289_An_Investigation_into_Unintentional_Information_Leakage_through_Electronic_Publication)

[Hill et al., used hidden Markov models to recover text obscured either by mosaic pixelization or a related tactic, e.g. Gaussian Blur](https://cseweb.ucsd.edu/~saul/papers/pets16-redact.pdf)

[While Müller et al. do not explicitly tackle redaction, they discuss hidden information present in PDF documents, specifically PDF document revision information and author name metadata.](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_1B-2_23109_paper.pdf)

[The Australian Cyber Security Center analyzed Adobe Acrobat 2017’s redaction security and considered several features including encryption, CMap leaks, redactions of text metadata, images, revision metadata, and form metadata](https://www.cyber.gov.au/sites/default/files/2023-03/PROTECT%20-%20An%20Examination%20of%20the%20Redaction%20Functionality%20of%20Adobe%20Acrobat%20Pro%20DC%202017%20%28October%202021%29.pdf)

[The National Security Agency’s redaction guide does not mention glyph positioning information but notes any underlying redacted text should be removed from the document before producing a PDF.](https://sgp.fas.org/othergov/dod/nsa-redact.pdf)

[The primary predecessor to our work is Lopresti and Spitz ](https://www.cse.lehigh.edu/~lopresti/Publications/2004/hdp04a.pdf) which presents a manual technique for matching glyphs to a redaction’s width in a raster image of text.

### 26 Oct '23

https://www.rijksoverheid.nl/onderwerpen/wet-open-overheid-woo
https://link.springer.com/chapter/10.1007/978-3-031-43849-3_28
https://books.google.nl/books?hl=en&lr=&id=HK7YEAAAQBAJ&oi=fnd&pg=PA310&dq=redacted+text+recognition+&ots=vAhoTFLm48&sig=hN3cESzDT3y9vU7uMV9j54SpAX4&redir_esc=y#v=onepage&q=redacted%20text%20recognition&f=false

#### Meeting met Maarten en Gensi

popluar, xpdf
donderdag planning inleveren.
schrijven en praktijk tegelijkertijd

### 25 Oct '23

#### [What are rule based systems?](https://www.scaler.com/topics/rule-based-system-in-ai/)

- AI bases choices or inferences on established rules.
- Expert and decision support systems?
- **Relies on a collection of predetermined rules to decide what to do next.**
- Rules are written in 'simple' human language for easy troubleshoot and maintance.
- Given a set of inputs, RBS will always create the same output; predictable and dependable; **determinism**
- **Scalable**
- Can be modified or updated more easily because rules can be divided into smaller components.
- Collection of inputs + rules = output.

Rule based systems consist of seven fundamental elements

- Knowledge base: rules; IF(cond) THEN(action).
- Database: collection of facts compared to the knowledge base's rules if (cond.) clause.
- The inference engine: derive logic and arrive at a conclusion; connect the facts from the database with the rules specified in the knowledge base; semantic reasoner; match-resolve-act loop.

- Explanations facilities

- User interface

- External connection

- Active recall

https://link.springer.com/chapter/10.1007/978-3-031-43849-3_28

Imagnet:

> ImageNet is an image database organized according to the WordNet hierarchy (currently only the nouns), in which each node of the hierarchy is depicted by hundreds and thousands of images. The project has been instrumental in advancing computer vision and deep learning research. The data is available for free to researchers for non-commercial use.

> ImageNet is an image dataset organized according to the WordNet hierarchy. Each meaningful concept in WordNet, possibly described by multiple words or word phrases, is called a "synonym set" or "synset". There are more than 100,000 synsets in WordNet; the majority of them are nouns (80,000+). In ImageNet, we aim to provide on average 1000 images to illustrate each synset. Images of each concept are quality-controlled and human-annotated. In its completion, we hope ImageNet will offer tens of millions of cleanly labeled and sorted images for most of the concepts in the WordNet hierarchy.

Image segmentation, semantic segmentation, instance segmentation.

**Semantic segmentation is important**; the process of classifying areas of interest in an image on a pixel-level basis. [a similiar example](https://medium.com/@kennethcassel/using-machine-learning-to-redact-personal-identifying-information-b95b53b935a9). You create a mask or map image and pass it into a deep learning model along-side the original image. Model learns from this labeled data and be able to predict what pixels in a new image are; training data used to pass into neural models to recognize redacted text in provided image.
[example](https://www.youtube.com/watch?v=uiE56h5LyXc). **Training data to train our neural model(s) and a dataset to test it on.**

**Semantic segmentation overview [link](https://www.youtube.com/watch?v=uiE56h5LyXc)**.

1. label your data
2. Create two datastores
3. Partition datastores (train, test)
4. import pretrained model and modify it
5. Train and evaluate

**[hard negative examples](https://www.reddit.com/r/computervision/comments/2ggc5l/what_is_hard_negative_mining_and_how_is_it/)**:

> Let's say I give you a bunch of images that contain one or more people, and I give you bounding boxes for each one. Your classifier will need both positive training examples (person) and negative training examples (not person).
> For each person, you create a positive training example by looking inside that bounding box. But how do you create useful negative examples?
> A good way to start is to generate a bunch of random bounding boxes, and for each that doesn't overlap with any of your positives, keep that new box as a negative.
> Ok, so you have positives and negatives, so you train a classifier, and to test it out, you run it on your training images again with a sliding window. But it turns out that your classifier isn't very good, because it throws a bunch of false positives (people detected where there aren't actually people).
> **A hard negative is when you take that falsely detected patch, and explicitly create a negative example out of that patch, and add that negative to your training set. When you retrain your classifier, it should perform better with this extra knowledge, and not make as many false positives.**

### Plan

1. Creating dataset; looking for pre-labeld datasets; creating our own handlabelled images (labelbox and then creating one mask image using Pillow).

2. Train an existing model [this one](https://huggingface.co/tasks/image-segmentation)

3. Test data

4. Evaluate

5. ...

### Questions

- Object detection, image/semantic segmentation, panoptic segmentation?
