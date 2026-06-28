from collections.abc import Iterator
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from spacy.language import Language
from spacy.tokens import Doc, Span
from .entity_mapper import (
    BaseEntityMapper,
    EntityResult,
    GLINER_MAPPER,
    GLINER2_MAPPER,
    HF_NER_MAPPER,
    OPENMED_MAPPER,
)

DOC_BUILDER_DEFAULT_SPANS_KEY = "sc"

class DocBuilder:
    """Utility for building spacy docs with entities for anonymacy pipelines."""
    def __init__(
        self,
        nlp: Language,
        text: str,
        *,
        label_mapping: Optional[Dict[str, str]] = None,
        spans_key: Optional[str] = DOC_BUILDER_DEFAULT_SPANS_KEY,
        annotate_ents: bool = False,
        default_score: float = 0.5,
    ):
        self.nlp = nlp
        self.doc = self.nlp._ensure_doc(text)
        self.spans_key = spans_key
        self.annotate_ents = annotate_ents
        self.label_mapping = label_mapping if label_mapping else {}
        self.default_score = default_score

    @classmethod
    def build_batch(
        cls,
        nlp: Language,
        texts: List[str],
        context_words: Optional[List[str]] = None,
        entities_list: Optional[List[Any]] = None,
        entity_mapper: Optional[BaseEntityMapper] = None,
        alignment_mode: str = "strict",
        **builder_kwargs
    ) -> Iterator[Doc]:
        """Build batch of docs with custom entities.

        Args:
            nlp: spaCy Language pipeline.
            texts: List of document texts.
            context_words: Optional context terms added to each doc.
            entities_list: Optional list of entity dicts, one per text.
                           Each entry may be a list of dicts (raw or
                           pre-mapped) or None.
            entity_mapper: Optional mapper to normalize entity dicts.
            alignment_mode: Passed to ``doc.char_span``.

        Returns:
            Iterator of spaCy Docs with spans populated.
        """
        if entities_list is None:
            entities_list = [None] * len(texts)

        for text, entities in zip(texts, entities_list):
            builder = cls(nlp, text, **builder_kwargs)
            if context_words:
                builder = builder.with_context_words(context_words)

            if entities:
                if entity_mapper:
                    mapped_result = entity_mapper.map(entities, builder.default_score)
                else:
                    mapped_result = entities
                builder = builder.with_entities(
                    mapped_result, alignment_mode=alignment_mode
                )

            yield builder.build()

    @classmethod
    def build_batch_gliner(cls, nlp: Language, texts: List[str], entities_list: List[Any], **kwargs) -> Iterator[Doc]:
        """Build batch of docs from GLiNER ``predict_entities()`` output."""
        return cls.build_batch(nlp, texts, entities_list=entities_list, entity_mapper=GLINER_MAPPER, **kwargs)

    @classmethod
    def build_batch_transformers(cls, nlp: Language, texts: List[str], entities_list: List[Any], **kwargs) -> Iterator[Doc]:
        """Build batch of docs from HuggingFace NER pipeline output."""
        return cls.build_batch(nlp, texts, entities_list=entities_list, entity_mapper=HF_NER_MAPPER, **kwargs)

    @classmethod
    def build_batch_gliner2(cls, nlp: Language, texts: List[str], entities_list: List[Any], **kwargs) -> Iterator[Doc]:
        """Build batch of docs from GLiNER2 ``extract_entities()`` output."""
        return cls.build_batch(nlp, texts, entities_list=entities_list, entity_mapper=GLINER2_MAPPER, **kwargs)

    @classmethod
    def build_batch_openmed(cls, nlp: Language, texts: List[str], entities_list: List[Any], **kwargs) -> Iterator[Doc]:
        """Build batch of docs from OpenMed PredictionResult output. Calls ``.to_dict()`` on each result."""
        converted = [r.to_dict() if r else {} for r in entities_list]
        return cls.build_batch(nlp, texts, entities_list=converted, entity_mapper=OPENMED_MAPPER, **kwargs)

    def with_gliner(self, entities: List[Any], alignment_mode: str = "strict") -> "DocBuilder":
        """Add GLiNER entities. Output of ``model.predict_entities()`` passed directly."""
        return self.with_entities(entities, GLINER_MAPPER, alignment_mode)

    def with_transformers(self, entities: List[Any], alignment_mode: str = "strict") -> "DocBuilder":
        """Add HuggingFace NER pipeline entities. Supports both ``entity`` and ``entity_group`` keys."""
        return self.with_entities(entities, HF_NER_MAPPER, alignment_mode)

    def with_gliner2(self, result: Dict[str, Any], alignment_mode: str = "strict") -> "DocBuilder":
        """Add GLiNER2 entities. Pass the dict returned by ``extract_entities()`` directly."""
        return self.with_entities(result, GLINER2_MAPPER, alignment_mode)

    def with_openmed(self, result: Any, alignment_mode: str = "strict") -> "DocBuilder":
        """Add OpenMed entities. Calls ``.to_dict()`` on the PredictionResult before mapping."""
        return self.with_entities(result.to_dict() if result else {}, OPENMED_MAPPER, alignment_mode)

    def with_context_words(self, context_words: List[str]) -> "DocBuilder":
        """Add _context to the doc with the provided context words."""
        self.doc._.context_words = context_words
        return self

    def with_entities(self, entities: Any, entity_mapper: Optional[BaseEntityMapper] = None, alignment_mode: str = "strict") -> "DocBuilder":
        """Add custom entities to the doc with specified label and score keys."""
        
        if not entities:
            return self
        mapped_result = entity_mapper.map(entities, self.default_score) if entity_mapper else entities
        spans = self._create_spans_from_entities(mapped_result, alignment_mode=alignment_mode)
        return self._apply_spans(spans)

    def _create_spans_from_entities(
        self,
        entities: List[EntityResult],
        alignment_mode: str = "strict"
    ) -> List[Span]:
        """Private helper: create spans from normalized entities."""
        spans = []
        for entity in entities:
            label = self.label_mapping.get(entity["label"], entity["label"])
            
            span = self.doc.char_span(
                entity["start"],
                entity["end"],
                label=label,
                alignment_mode=alignment_mode
            )
            if span is None:
                continue

            span._.score = min(float(entity.get("score", self.default_score)), 1.0)
            spans.append(span)
        return spans

    def _apply_spans(self, spans: List[Span]) -> "DocBuilder":
        """Private helper: apply spans to doc."""
        if spans:
            if self.spans_key:
                all_spans = list(self.doc.spans.get(self.spans_key, []))
                all_spans.extend(spans)
                self.doc.spans[self.spans_key] = all_spans
            
            if self.annotate_ents:
                all_ents = list(self.doc.ents)
                all_ents.extend(spans)
                self.doc.ents = tuple(all_ents)
        
        return self

    def build(self) -> Doc:
        """Return the built Doc with spans."""
        return self.doc