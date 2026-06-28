# Multi-word context phrases translated as per-token LEMMA sequences

Presidio's `context` list contains strings like `"australian business number"`. `translate_context` splits multi-word phrases into a list of per-token `{"LEMMA": word}` dicts so spaCy's phrase matcher can match them across token boundaries. Single words are batched into a single `{"LEMMA": {"IN": [...]}}` pattern for efficiency.

A single `{"LEMMA": "australian business number"}` dict would never match because spaCy matches token-by-token — there is no single token with that lemma.

## Considered Options

- **Single dict per phrase**: simple to generate, but silently never matches multi-word phrases in practice.
- **Per-token sequence** (chosen): correctly matches multi-word phrases at the cost of one pattern dict per word in the phrase.
