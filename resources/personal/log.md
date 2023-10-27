# Logbook

### 27 Oct '23

#### (11:00-13:30) Research on PDF file extension: 

[Stackoverflow discussion on how to inspect the structure of PDF files](https://stackoverflow.com/questions/3549541/how-can-i-visually-inspect-the-structure-of-a-pdf-to-reverse-engineer-it)

[A high performance Python library for data extraction, analysis, conversion & manipulation of PDF (and other) documents.](https://pypi.org/project/PyMuPDF/)

[PDF 1.4 specifications](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.4.pdf)

#### (8:30-11:00) *Bland_EdactRay_2022.pdf* notes:

Security of PDF document depends on the specification. A **raster image** of the original document or a document type that contains text data for both the font and the layout of each character (**glyph**) on the page.

Text is rendered in numerous ways. An example is by use of a **text showing operator**. It takes as arguments a **(1)string of text** and a **(2)vector of positional adjustments** which displace the charachter with respect to a default position, usually **a fixed offset from the previous character equivalent to the advance width of the previous character defined elsewhere in the PDF document**

Paper introduces a intermediate representation; **a set of advance widths and glyph shifts** which are the sum of all the individual positioning operations applied to a glyph.

Positional adjustments in *text space units* between glyphs. These units express **glyph shifts** where 1000 units almost always equals the point size of the fint times 1/72 of an inch. 

Glyph advance widths and glyph shifts create a security concern:
1. The precise width of the redaction can be used to eliminate potential redacted texts
2. Any non-redacted glyph shifts conditioned on redacted glyphs can be used to eliminate
potential redacted texts 

> The width of a PDF redaction depends on glyph shifts. Without accounting for glyph shifts, redacted text guesses are imprecise and must account for error, reducing the potential of finding a unique match for redacted content. *The width of a PDF redaction depends on glyph shifts. Without accounting for glyph shifts, redacted text guesses are imprecise and must account for error, reducing the potential of finding a unique match for redacted content*

##### Glyph Shifts

Glyph shifts in PDF document are dependent on the specific workflow from a *PDF producer* by the ISO 32000 PDF standard, and any software that may modify the PDF.

**Independent glyph shifts** for a given character are not dependent on any other character, while **dependent glyph shifts** are dependent on some other charachter in the document in some way. These are called **glyph shifting schemes** that are created by a specific workflow. Independent schemes are *unadjusted* when there are no shifts on any character.

*Equivalence Classes. Before discussing these schemes further, we introduce the idea of width and shift equivalence classes. A shift equivalence class is a set of lists of glyphs of the same length with identical shift values. A width equivalence class is a set of glyphs and associated shifts with the same width*

> The PDF specification does not include any specific signifiers for redacted text. However, residual specification information after redaction, such as glyph positions, can be used to reasonably rule out large numbers of candidate width and shift equivalence classes for redacted text. None of the prior words in this paragraph are in the width equivalence class of the word cat.

*In an independent glyph shifting scheme, the security of a redaction may be considered dependent on the size of the width equivalence class indiscated by the PDF document’s residual glyph positioning information. That is, the positions of glyphs prior to and succeeding the redaction may leak the width of redacted text. The scheme’s specific glyph shifts can make a given width equivalence class leak more or less redacted information by making width of individual glyphs more or less unique.*

*Dependent Schemes.A dependent scheme is more dangerous to the security of redacted text than an independent scheme. In these schemes non-redacted glyph shifts can be dependent upon redacted glyph information, because the non-redacted glyph shifts can be determined before redaction*

##### Protecting Redactions 

> *"Edact-Ray protects vulnerable PDF redactions by first locating the nonexcising redactions and removing their underlying text from the PDF. We then adopt a userconfigurable level of information excisement by allowing users to optionally remove all non-redacted glyph shifts13 and optionally convert the font to a monospaced one, scaling the size to preserve readability. To protect excising redactions, Edact-Ray can round up the size of all spaces between two words to some width, 𝑛 × 𝑤, where 𝑛 is some number of characters and 𝑤 is width of a single character in the monospace font. Edact-Ray can also remove any rectangular draw commands from the PDF so that the width of the redaction cannot be recovered by examining the width of any graphical box drawn to represent the redaction."*

(!) Monospace font?

##### Recommended practices

> Redaction practices must account for concerns about document integrity. All the above measures
modify the redacted document beyond simply removing text. In some contexts, particularly due
to legal or regulatory reasons, this may not be acceptable. One of the main reasons for releasing
redacted documents is to demonstrate transparency while still protecting sensitive information.
Altering parts of the document outside the redaction alters this promise of authenticity.

> It is technically possible to fix a non-excising redaction by removing the redacted text. The effect would be the same as if the document were redacted by an excising redaction tool. However, this also raises the issue of authenticity of done by a third party (e.g. document repository operator), because this necessarily means modifying the original document without the author’s involvement. In cases where integrity requirements may be relaxed, the NSA-recommended practice of altering the original document to replace the redacted text with meaningless text, e.g. REDACTED, provides the highest level of security.

> In cases where the underlying text may not be changed, we offer the following two suggestions.
First, we note that redacting a name from a PDF is not secure. If a name occurs on a line of
text, the entire line should be redacted, if possible, or care should be taken to ensure that enough of the surrounding words are redacted to make deredaction unlikely. Second, if redacting more text is not possible, the width of the redaction should be quantized to a fixed value, and any glyph shifts should be removed. While this may make the file less aesthetically pleasing, it is necessary for the security of redactions.

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
