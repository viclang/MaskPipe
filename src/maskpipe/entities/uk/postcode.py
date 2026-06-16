"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_postcode_recognizer.UkPostcodeRecognizer."""
from maskpipe.entities.entity import Entity

UK_POSTCODE = Entity(
    label="UK_POSTCODE",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b(GIR\s?0AA|[A-PR-UWYZ][0-9][ABCDEFGHJKPSTUW]?\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]?\s?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2})\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["postcode", "post code", "postal code", "zip", "address", "delivery", "mailing", "shipping", "correspondence"]}}], "score": 0.35},
    ],
)
