"""Entity generated from presidio_analyzer.predefined_recognizers.generic.email_recognizer.EmailRecognizer."""
from spacy.tokens import Span
import tldextract
from maskpipe.entities.entity import Entity

def _validator(span: Span):
    pattern_text = span.text
    result = tldextract.extract(pattern_text)
    return result.fqdn != ''

EMAIL_ADDRESS = Entity(
    label="EMAIL_ADDRESS",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["email"]}}], "score": 0.35},
    ],
)
