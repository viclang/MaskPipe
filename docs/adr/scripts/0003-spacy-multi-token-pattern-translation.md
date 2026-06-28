# spaCy multi-token pattern translation for Presidio regex separators

When a Presidio regex contains separator characters that spaCy's tokenizer splits on (hyphens, spaces, dots, slashes — e.g. `\d{3}[- ]\d{2}`), `translate_pattern` emits two spaCy patterns: a single-token `TEXT: REGEX` pattern (for tokenizers that keep the string together) and a multi-token pattern where each segment is a separate token dict and the separator becomes an optional `{"TEXT": "-", "OP": "?"}` token.

A single regex pattern cannot cover both behaviours because spaCy tokenization is language-dependent: Dutch and Spanish tokenizers keep hyphens attached, English splits on them.

## Considered Options

- **Single-token only**: misses multi-token splits for English and other languages that split on separators.
- **Multi-token only**: misses languages that keep the string together.
- **Both patterns** (chosen): covers all tokenizer behaviours at the cost of producing two patterns per Presidio regex that contains a separator.
