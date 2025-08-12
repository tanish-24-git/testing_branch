import logging
from sentence_transformers import SentenceTransformer
import spacy

logger = logging.getLogger(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2')  # For vectorization/tokenization
nlp = spacy.load("en_core_web_sm")  # For NLP intent/entity extraction

def vectorize_text(text: str):
    """Vectorize text for semantic search."""
    return model.encode(text)

def extract_intent_entities(command):
    """Use spaCy to extract intent and entities."""
    doc = nlp(command)
    intent = doc[0].lemma_ if doc else "unknown"  # Simple heuristic: first verb as intent
    entities = {ent.label_: ent.text for ent in doc.ents}
    return intent, entities

def placeholder_function():
    """Placeholder utility function."""
    logger.info("Utility function called")
    return None