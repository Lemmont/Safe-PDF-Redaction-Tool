# Week 1: Literature & PDF research, and projectplan

## Tasks

1. ~~Formulate problem for Thesis.~~
2. ~~Formulate first version of _introduction_ section for Thesis.~~
3. ~~Research possible solutions? Just look at literature and re-read already found stuff~~
4. ~~Finish _projectplan_.~~

## Findings

Focus on one specific field of text redaction in PDF files: Wet openbare overheid field?

## Code stuff

https://pypi.org/project/fpdf2/

    Simple & fast PDF generation for Python

https://pypi.org/project/PyMuPDF/

    A high performance Python library for data extraction, analysis, conversion & manipulation of PDF (and other) documents.

https://pypdf.readthedocs.io/en/latest/

    pypdf is a free and open source pure-python PDF library capable of splitting, merging, cropping, and transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF files. pypdf can retrieve text and metadata from PDFs as well.

## Literature

### Security Concerns

[PDF redaction is broken by Glyph Positions](https://arxiv.org/abs/2206.02285v3)(2023)

    adresses subpixel-sized horizontal shifts (Glyph Positions).

[The primary predecessor to our work is Lopresti and Spitz ](https://www.cse.lehigh.edu/~lopresti/Publications/2004/hdp04a.pdf)

    to be added...

[Forrester and Irwin discuss trivial redactions and unscrubbed metadata such as the Producer field of PDF documents but do not mention glyph positioning based deredaction](https://www.researchgate.net/publication/229014289_An_Investigation_into_Unintentional_Information_Leakage_through_Electronic_Publication) (5 cites/2005)

    adresses unscrubbed metadata and trivial redactions (just a black box masking text).

[On security and Privacy of The PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_1B-2_23109_paper.pdf) (6 cites/2021)

    adresses hidden data: evitable metadata and revision recovery.

[The National Security Agency’s redaction guide](https://sgp.fas.org/othergov/dod/nsa-redact.pdf) (2005)

    adresses that text often is just masked with a black box and text is left in document.

[Hill et al., used hidden Markov models to recover text obscured either by mosaic pixelization or a related tactic, e.g. Gaussian Blur](https://cseweb.ucsd.edu/~saul/papers/pets16-redact.pdf) (2016)

    adresses that redaction through mosaicing/pixelation and blurring is broken by hidden Markov Models. Not a viable option.

[What you see is not what you get in the PDF document; What you see is what you store](https://journals.sagepub.com/doi/full/10.1177/1460458210397851#bibr3-1460458210397851)

    adresses redacted text often not being deleted but just a black box masking it.

[Wooverheid](https://wooverheid.nl/2023/09/22/niet-zo-toegankelijke-besluiten/)

[Openbaarheid van bestuur kan vrijwel kosteloos beter](https://esb.nu/openbaarheid-van-bestuur-kan-vrijwel-kosteloos-beter/)

[Stukken vrijgegeven onder de Woo Niet goed toegankelijk](https://magazines.od-online.nl/od-28-2023/niet-goed-toegankelijk)

### More on Woo and legality

[Enticing Local Governments to Produce FAIR Freedom of Information Act Dossiers](https://link.springer.com/chapter/10.1007/978-3-031-28241-6_25)

### For possible solution

[Toward an Extensible Framework for Redaction](https://seclab.illinois.edu/wp-content/uploads/2018/06/demetriou2018toward.pdf) (2018) (cited by 0) (2023) (cited by 0)

    to be added...

### For possible testing

[X-Ray Bad Redaction Detector](https://github.com/freelawproject/x-ray)

    finds bad redactions in PDF. Non-excising redactions!

[Edact-Ray Tool Suite](https://github.com/maxwell-bland/deredaction)

    finds bad redactions in PDF. Both non-excising and excising redactions. Need to ask for code.

> _If you are a scholart, email me and I can give you the full code and datasets on valid scientific request, for reproduction purposes and to make your research easier!There are also lots of small easter eggs buried around this repository that may help future research._
