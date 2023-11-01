# Week 1: Literature & PDF research, and projectplan

## Tasks

1. Formulate problem for Thesis.
2. Formulate first version of _related work_ section for Thesis.
3. Research possible solutions? Just look at literature and re-read already found stuff

4. Finish _projectplan_.

## Literature

### Security Concerns

[PDF redaction is broken by Glyph Positions](https://arxiv.org/abs/2206.02285v3)(2023)

    adresses subpixel-sized horizontal shifts (Glyph Positions).

[Forrester and Irwin discuss trivial redactions and unscrubbed metadata such as the Producer field of PDF documents but do not mention glyph positioning based deredaction](https://www.researchgate.net/publication/229014289_An_Investigation_into_Unintentional_Information_Leakage_through_Electronic_Publication) (5 cites/2005)

    adresses unscrubbed metadata and trivial redactions (just a black box masking text).

[On security and Privacy of The PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_1B-2_23109_paper.pdf) (6 cites/2021)

    adresses hidden data: evitable metadata and revision recovery.

[The National Security Agency’s redaction guide](https://sgp.fas.org/othergov/dod/nsa-redact.pdf) (2005)

    adresses that text often is just masked with a black box and text is left in document.

[Hill et al., used hidden Markov models to recover text obscured either by mosaic pixelization or a related tactic, e.g. Gaussian Blur](https://cseweb.ucsd.edu/~saul/papers/pets16-redact.pdf) (2016)

    adresses that redaction through mosaicing/pixelation and blurring is broken by hidden Markov Models. Not a viable option.
