"""Entity generated from presidio_analyzer.predefined_recognizers.generic.phone_recognizer.PhoneRecognizer."""

# BEGIN GENERATED: imports
from phonenumbers.phonenumberutil import NumberParseException
from spacy.tokens import Doc
import phonenumbers
from maskpipe.entities.entity import ContextPattern, Entity
# END GENERATED: imports

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: custom_matcher
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
# END GENERATED: custom_matcher

PHONE_NUMBER = Entity(
    label="PHONE_NUMBER",
    custom_matcher=_custom_matcher,
    context_patterns=_CONTEXT_PATTERNS,
)
