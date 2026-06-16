"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_mbi_recognizer.UsMbiRecognizer."""
from maskpipe.entities.entity import Entity

US_MBI = Entity(
    label="US_MBI",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b[0-9][ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9][ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9][ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY][0-9][0-9]\b"}}]},
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[0-9][ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9]-[ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9]-[ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY][0-9][0-9]\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b[0-9][ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9]\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b[ACDEFGHJKMNPQRTUVWXY][0-9ACDEFGHJKMNPQRTUVWXY][0-9]\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b[ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY][0-9][0-9]\b"}},
        ]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["medicare", "mbi", "beneficiary", "cms", "medicaid", "hic", "hicn"]}}], "score": 0.35},
    ],
)
