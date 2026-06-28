# Sampling is reproducible by default via DEFAULT_RANDOM_STATE

`analyze()` samples column values randomly. Without a fixed seed, the same column can flip between labels across runs depending on which rows were drawn, making results difficult to debug and tests non-deterministic.

`random_state` defaults to `DEFAULT_RANDOM_STATE` (123), matching the convention used by Presidio's `AnalysisBuilder`. Callers pass `None` to opt into non-deterministic behaviour. A local `random.Random` instance is used rather than `random.seed()` to avoid mutating global state, which is not thread-safe.

The value 123 carries no special meaning; it was chosen to be consistent with Presidio so that shared notebooks and examples produce identical results without callers needing to coordinate seeds.
