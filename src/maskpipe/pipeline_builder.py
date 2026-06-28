from typing import (
    Any,
    Dict,
    List,
    Optional,
    cast,
)

from spacy.language import Language

from .anonymizer import Anonymizer
from .context_enhancer import ContextEnhancer
from .entities.entity import Entity
from .recognizer import Recognizer

def partition_entities(
    entities: List[Entity],
    components: List[str],
    label_mapping: Dict[str, str],
) -> Dict[str, Dict[str, Any]]:
    batch: Dict[str, Dict[str, Any]] = {
        "recognizer": {"patterns": [], "custom_matchers": {}, "validators": {}},
        "context_enhancer": {"patterns": []},
        "anonymizer": {"redactors": {}},
    }
    for entity in entities:
        label = label_mapping.get(entity.label, entity.label)

        if "recognizer" in components:
            if entity.patterns:
                batch["recognizer"]["patterns"].extend(
                    {**pattern, "label": label} for pattern in entity.patterns
                )
            if entity.custom_matcher:
                batch["recognizer"]["custom_matchers"][label] = entity.custom_matcher
            if entity.validator:
                batch["recognizer"]["validators"][label] = entity.validator

        if "context_enhancer" in components:
            if entity.context_patterns:
                batch["context_enhancer"]["patterns"].extend(
                    {**pattern, "label": label} for pattern in entity.context_patterns
                )

        if "anonymizer" in components:
            if entity.redactor:
                batch["anonymizer"]["redactors"][label] = entity.redactor

    return batch


class PipelineBuilder:
    """Minimal API every language builder must honour."""
    
    def __init__(
            self,
            nlp: Language,
            *,
            label_mapping: Optional[Dict[str, str]] = None,
            disable: Optional[List[str]] = None
        ):
        self.components = ["recognizer", "context_enhancer", "conflict_resolver", "anonymizer"]
        self.nlp = nlp
        self.label_mapping = label_mapping if label_mapping else {}
        disabled = set(disable) if disable else set()
        self.components = [c for c in self.components if c not in disabled]

        for component in disabled:
            if nlp.has_pipe(component):
                nlp.remove_pipe(component)

        for component in self.components:
            if not nlp.has_pipe(component):
                nlp.add_pipe(component)
        
    def add_entities(self, entities: List[Entity]):
        """Partition entities and add their patterns, matchers, and redactors to relevant components."""

        batch = partition_entities(entities, self.components, self.label_mapping)

        if "recognizer" in self.components:
            recognizer = cast(Recognizer, self.nlp.get_pipe("recognizer"))
            recognizer.add_patterns(batch["recognizer"]["patterns"])
            recognizer.add_custom_matchers(batch["recognizer"]["custom_matchers"])
            recognizer.add_validators(batch["recognizer"]["validators"])

        if "context_enhancer" in self.components:
            context_enhancer = cast(ContextEnhancer, self.nlp.get_pipe("context_enhancer"))
            context_enhancer.add_patterns(batch["context_enhancer"]["patterns"])
        
        if "anonymizer" in self.components:
            anonymizer = cast(Anonymizer, self.nlp.get_pipe("anonymizer"))
            anonymizer.add_redactors(batch["anonymizer"]["redactors"])

    def build(self) -> Language:
        """Return the configured Language object.
        
        Use the returned nlp object with process_with_entities() or pipe_with_entities()
        from anonymacy.processing for entity processing.
        
        Returns:
            The configured Language object.
        """
        return self.nlp