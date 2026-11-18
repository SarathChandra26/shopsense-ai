import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Ensure TensorFlow backend is bypassed
os.environ["TRANSFORMERS_NO_TF"] = "1"

_EMBEDDER_INSTANCE: Optional["ProductEmbedder"] = None

class ProductEmbedder:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        logger.info(f"Initializing SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = settings.EMBEDDING_DIMENSION
        logger.info("SentenceTransformer model loaded successfully.")

    @staticmethod
    def build_searchable_text(product: Dict[str, Any]) -> str:
        """
        Construct rich semantic text representation for dense retrieval.
        Combines: Name, Brand, Category, Description, and Structured Specifications.
        """
        name = product.get("name", "")
        brand = product.get("brand", "")
        category = product.get("category", "")
        description = product.get("description", "")
        
        specs = product.get("specifications", {})
        if isinstance(specs, str):
            try:
                import json
                specs = json.loads(specs)
            except Exception:
                specs = {}
                
        specs_str_parts = []
        for k, v in specs.items():
            clean_k = k.replace("_", " ").title()
            specs_str_parts.append(f"{clean_k}: {v}")
        specs_text = "; ".join(specs_str_parts)

        searchable_text = (
            f"Product: {name}. Brand: {brand}. Category: {category}. "
            f"Key Specs: {specs_text}. "
            f"Overview: {description}"
        )
        return searchable_text

    def encode_text(self, text: str) -> List[float]:
        """Generate normalized embedding for a single text."""
        emb = self.model.encode(text, normalize_embeddings=True)
        return emb.tolist()

    def encode_batch(self, texts: List[str], batch_size: int = settings.EMBEDDING_BATCH_SIZE) -> List[List[float]]:
        """Generate normalized embeddings for a batch of texts."""
        if not texts:
            return []
        embs = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embs.tolist()

def get_embedder() -> ProductEmbedder:
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        _EMBEDDER_INSTANCE = ProductEmbedder()
    return _EMBEDDER_INSTANCE
