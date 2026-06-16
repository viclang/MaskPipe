"""Entity generated from presidio_analyzer.predefined_recognizers.generic.phone_recognizer.PhoneRecognizer."""
from spacy.tokens import Doc
from phonenumbers.phonenumberutil import NumberParseException
import phonenumbers
from maskpipe.entities.entity import Entity

def _analyze(text: str):
    results = []
    for region in ('US', 'UK', 'DE', 'FE', 'IL', 'IN', 'CA', 'BR'):
        for match in phonenumbers.PhoneNumberMatcher(text, region, leniency=1):
            try:
                parsed_number = phonenumbers.parse(text[match.start:match.end])
                region = phonenumbers.region_code_for_number(parsed_number)
                results += [(match.start, match.end, 0.4)]
            except NumberParseException:
                results += [(match.start, match.end, 0.4)]
    return results

def _custom_matcher(doc: Doc) -> list[tuple[int, int, float]]:
    spans = []
    for char_start, char_end, score in _analyze(doc.text):
        span = doc.char_span(char_start, char_end, alignment_mode="expand")
        if span:
            spans.append((span.start, span.end, score))
    return spans

PHONE_NUMBER = Entity(
    label="PHONE_NUMBER",
    custom_matcher=_custom_matcher,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"]}}], "score": 0.35},
    ],
)
