import random
from collections import defaultdict
from collections.abc import Iterable
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NotRequired,
    Optional,
    Set,
    TypedDict,
)
from spacy.language import Language
from spacy.tokens import Span
from .constants import SPANS_KEY
from .doc_builder import DocBuilder
from .entity_mapper import (
    BaseEntityMapper,
    EntityResult,
    GLINER_MAPPER,
    GLINER2_MAPPER,
    HF_NER_MAPPER,
    OPENMED_MAPPER,
)
from .span_filter import hierarchical_merge_filter

NON_PII_LABEL = "NON_PII"
DEFAULT_RANDOM_STATE = 123

class LabelStats(TypedDict):
    coverage: float
    score: float

class ColumnAnalysis(TypedDict):
    label: str
    score: float  # coverage × average entity confidence for the winning label
    entity_distribution: Dict[str, LabelStats]
    entities: NotRequired[List[EntityResult]]

SpansFilterFunc = Callable[[Iterable[Span]], Iterable[Span]]

class StructuredAnalyzer:

    def __init__(
        self,
        nlp: Language,
        *,
        label_mapping: Optional[Dict[str, str]] = None,
        spans_key: str = SPANS_KEY,
        spans_filter: SpansFilterFunc = hierarchical_merge_filter,
        default_score: float = 0.6,
    ):
        self.nlp = nlp
        self.label_mapping = label_mapping
        self.spans_key = spans_key
        self.spans_filter = spans_filter
        self.default_score = default_score

    def analyze(
        self,
        data: Dict[str, List[Any]],
        batch_extractor: Optional[Callable[[List[str]], List[Any]]] = None,
        *,
        n: Optional[int] = None,
        entity_mapper: Optional[BaseEntityMapper] = None,
        alignment_mode: str = "strict",
        random_state: Optional[int] = DEFAULT_RANDOM_STATE,
        include_entities: bool = False,
    ) -> Dict[str, ColumnAnalysis]:
        if not data:
            return {}

        if n is None:
            first_values = next(iter(data.values()))
            if not first_values:
                return {}
            n = len(first_values)

        rng = random.Random(random_state)
        results: Dict[str, ColumnAnalysis] = {}

        for column, values in data.items():
            non_null_values = [v for v in values if v is not None and str(v).strip()]
            sample_size = min(n, len(non_null_values))
            sampled_values = [str(v) for v in rng.sample(non_null_values, sample_size)]

            extracted = (
                batch_extractor(sampled_values) if batch_extractor else None
            )
            docs = DocBuilder.build_batch(
                nlp=self.nlp,
                texts=sampled_values,
                context_words=[column],
                entities_list=extracted,
                entity_mapper=entity_mapper,
                alignment_mode=alignment_mode,
                label_mapping=self.label_mapping,
                spans_key=self.spans_key,
                default_score=self.default_score,
            )

            all_entities: List[EntityResult] = []
            cell_label_sets: List[Set[str]] = []

            for doc in self.nlp.pipe(docs):
                cell_label_set, doc_entities = self._process_doc(doc)
                cell_label_sets.append(cell_label_set)
                all_entities.extend(doc_entities)

            results[column] = self._classify_column(cell_label_sets, all_entities, include_entities)

        return results

    def analyze_gliner(
        self,
        data: Dict[str, List[Any]],
        batch_extractor: Callable[[List[str]], List[Any]],
        *,
        n: Optional[int] = None,
        alignment_mode: str = "strict",
        random_state: Optional[int] = DEFAULT_RANDOM_STATE,
        include_entities: bool = False,
    ) -> Dict[str, ColumnAnalysis]:
        """Analyze with GLiNER. ``batch_extractor`` should return raw ``predict_entities()`` output."""
        return self.analyze(
            data,
            batch_extractor=batch_extractor,
            n=n,
            entity_mapper=GLINER_MAPPER,
            alignment_mode=alignment_mode,
            random_state=random_state,
            include_entities=include_entities,
        )

    def analyze_transformers(
        self,
        data: Dict[str, List[Any]],
        batch_extractor: Callable[[List[str]], List[Any]],
        *,
        n: Optional[int] = None,
        alignment_mode: str = "strict",
        random_state: Optional[int] = DEFAULT_RANDOM_STATE,
        include_entities: bool = False,
    ) -> Dict[str, ColumnAnalysis]:
        """Analyze with HuggingFace NER pipeline output."""
        return self.analyze(
            data,
            batch_extractor=batch_extractor,
            n=n,
            entity_mapper=HF_NER_MAPPER,
            alignment_mode=alignment_mode,
            random_state=random_state,
            include_entities=include_entities,
        )

    def analyze_gliner2(
        self,
        data: Dict[str, List[Any]],
        batch_extractor: Callable[[List[str]], List[Any]],
        *,
        n: Optional[int] = None,
        alignment_mode: str = "strict",
        random_state: Optional[int] = DEFAULT_RANDOM_STATE,
        include_entities: bool = False,
    ) -> Dict[str, ColumnAnalysis]:
        """Analyze with GLiNER2. Unwraps the outer list from each result before mapping."""
        def _extract(texts: List[str]) -> List[Any]:
            return [r[0] if r else {} for r in batch_extractor(texts)]
        return self.analyze(
            data,
            batch_extractor=_extract,
            n=n,
            entity_mapper=GLINER2_MAPPER,
            alignment_mode=alignment_mode,
            random_state=random_state,
            include_entities=include_entities,
        )

    def analyze_openmed(
        self,
        data: Dict[str, List[Any]],
        batch_extractor: Callable[[List[str]], List[Any]],
        *,
        n: Optional[int] = None,
        alignment_mode: str = "strict",
        random_state: Optional[int] = DEFAULT_RANDOM_STATE,
        include_entities: bool = False,
    ) -> Dict[str, ColumnAnalysis]:
        """Analyze with OpenMed. Calls ``.to_dict()`` on each PredictionResult before mapping."""
        def _extract(texts: List[str]) -> List[Any]:
            return [r.to_dict() if r else {} for r in batch_extractor(texts)]
        return self.analyze(
            data,
            batch_extractor=_extract,
            n=n,
            entity_mapper=OPENMED_MAPPER,
            alignment_mode=alignment_mode,
            random_state=random_state,
            include_entities=include_entities,
        )

    def _process_doc(self, doc) -> tuple[Set[str], List[EntityResult]]:
        if doc.ents:
            ents = doc.ents
        else:
            raw_spans = doc.spans.get(self.spans_key, [])
            ents = self.spans_filter(raw_spans) if raw_spans else []
        if not ents:
            return set(), []

        unique_labels: Set[str] = set()
        entities: List[EntityResult] = []

        for ent in ents:
            unique_labels.add(ent.label_)
            entities.append(
                EntityResult(
                    start=ent.start_char,
                    end=ent.end_char,
                    label=ent.label_,
                    score=(
                        ent._.score
                        if ent.has_extension("score")
                        else self.default_score
                    ),
                )
            )

        return unique_labels, entities

    def _classify_column(
        self,
        cell_label_sets: List[Set[str]],
        all_entities: List[EntityResult],
        include_entities: bool,
    ) -> ColumnAnalysis:
        _empty = ColumnAnalysis(
            label=NON_PII_LABEL,
            score=0.0,
            entity_distribution={},
        )
        if not cell_label_sets:
            return _empty

        total_cells = len(cell_label_sets)
        non_pii_count = sum(1 for s in cell_label_sets if not s)

        if non_pii_count == total_cells:
            return _empty

        label_cell_counts: Dict[str, int] = defaultdict(int)
        for label_set in cell_label_sets:
            for label in label_set:
                label_cell_counts[label] += 1

        label_score_lists: Dict[str, List[float]] = defaultdict(list)
        for e in all_entities:
            label_score_lists[e['label']].append(e['score'])

        def avg_label_score(label: str) -> float:
            scores = label_score_lists.get(label, [])
            return sum(scores) / len(scores) if scores else 0.0

        entity_distribution: Dict[str, LabelStats] = {
            label: LabelStats(
                coverage=count / total_cells,
                score=avg_label_score(label),
            )
            for label, count in label_cell_counts.items()
        }

        column_label = max(
            label_cell_counts,
            key=lambda l: (label_cell_counts[l] / total_cells) * avg_label_score(l),
        )
        score = (label_cell_counts[column_label] / total_cells) * avg_label_score(column_label)

        result = ColumnAnalysis(
            label=column_label,
            score=score,
            entity_distribution=entity_distribution,
        )

        if include_entities:
            result['entities'] = all_entities

        return result
