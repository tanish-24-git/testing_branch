import logging
from sentence_transformers import SentenceTransformer
import spacy

logger = logging.getLogger(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2')  # For vectorization/tokenization
nlp = None  # Lazy-load spaCy

def load_nlp():
    """Load spaCy model only when needed."""
    global nlp
    if nlp is None:
        logger.info("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy model loaded")
    return nlp

def vectorize_text(text: str):
    """Vectorize text for semantic search."""
    return model.encode(text)

def extract_intent_entities(command):
    """Use spaCy to extract intent and entities."""
    doc = load_nlp()(command)
    intent = doc[0].lemma_ if doc else "unknown"  # Simple heuristic: first verb as intent
    entities = {ent.label_: ent.text for ent in doc.ents}
    return intent, entities

def placeholder_function():
    """Placeholder utility function."""
    logger.info("Utility function called")
    return None