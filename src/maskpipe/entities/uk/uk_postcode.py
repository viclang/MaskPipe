"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_postcode_recognizer.UkPostcodeRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b(GIR\s?0AA|[A-PR-UWYZ][0-9][ABCDEFGHJKPSTUW]?\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]?\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2})\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["postcode", "zip", "address", "delivery", "mailing", "shipping", "correspondence"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "post"}, {"LEMMA": "code"}], "score": 0.35},
    {"pattern": [{"LEMMA": "postal"}, {"LEMMA": "code"}], "score": 0.35},
]
# END GENERATED: context_patterns

UK_POSTCODE = Entity(
    label="UK_POSTCODE",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
