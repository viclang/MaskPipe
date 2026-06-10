# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#     "marimo>=0.23.3",
#     "maskpipe[presidio]",
# ]
#
# [tool.uv.sources]
# maskpipe = { path = "../", editable = true }
#
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # UsSsnRecognizer via PresidioConverter

    Wraps Presidio's `UsSsnRecognizer` as a maskpipe entity and runs it against the
    same test cases used in `test_presidio_parity.py`.

    All formats detected by both native maskpipe and the Presidio converter.
    ``PresidioConverter`` expands ``[- .]`` separator classes into multi-token patterns.

    | Format | Native | Presidio (converted) |
    |---|---|---|
    | `532431234` (no separator) | ✓ | ✓ |
    | `401.22.3456` (dot) | ✓ | ✓ |
    | `123-45-6789` (hyphen) | ✓ | ✓ |
    | `123 45 6789` (space) | ✓ | ✓ |
    """)
    return


@app.cell
def _():
    import marimo as mo
    from maskpipe import PipelineBuilder
    from maskpipe.presidio import PresidioConverter
    from maskpipe.entities.us.ssn import SSN
    from presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer import UsSsnRecognizer

    return PipelineBuilder, PresidioConverter, SSN, UsSsnRecognizer, mo


@app.cell
def _(PipelineBuilder, PresidioConverter, SSN, UsSsnRecognizer):
    from spacy.lang.en import English

    def build(entity):
        nlp = English()
        pipe = PipelineBuilder(nlp, disable=["context_enhancer", "anonymizer"])
        pipe.add_entities([entity])
        return nlp

    def detect(nlp, text):
        doc = nlp(text)
        return {s.text for s in doc.spans["sc"]}

    native_nlp = build(SSN)
    presidio_nlp = build(PresidioConverter().convert(UsSsnRecognizer()))

    print(PresidioConverter().convert(UsSsnRecognizer()))
    return detect, native_nlp, presidio_nlp


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Results by category
    """)
    return


@app.cell
def _(detect, mo, native_nlp, presidio_nlp):
    VALID_SSNS = [
        "532431234",
        "401223456",
        "532.43.1234",
        "532-43-1234",
        "532 43 1234"
    ]

    BOTH_REJECT = [
        "078051120",   # reserved test SSN
        "123456789",   # well-known test SSN
        "987654321",   # reserved
        "000123456",   # area code 000 invalid
        "666123456",   # area code 666 invalid
    ]

    # Presidio accepts these; native maskpipe rejects area codes 900-999
    NATIVE_STRICTER = [
        "912345678",
    ]

    def row(label, text):
        n = bool(detect(native_nlp, text))
        p = bool(detect(presidio_nlp, text))
        return {"SSN": text, "Category": label, "Native": "✓" if n else "✗", "Presidio": "✓" if p else "✗"}

    rows = (
        [row("valid", t) for t in VALID_SSNS]
        + [row("both reject", t) for t in BOTH_REJECT]
        + [row("native stricter", t) for t in NATIVE_STRICTER]
    )

    mo.ui.table(rows)
    return


if __name__ == "__main__":
    app.run()
