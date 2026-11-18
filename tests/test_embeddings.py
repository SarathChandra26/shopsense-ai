import pytest
from backend.app.embeddings.embedder import get_embedder, ProductEmbedder

def test_embedder_dimension_and_batch():
    embedder = get_embedder()
    assert embedder.dimension == 384

    text = "Dell XPS 15 laptop with 32 GB RAM for Python engineering"
    emb = embedder.encode_text(text)
    assert len(emb) == 384
    assert isinstance(emb[0], float)

    batch = [
        "Lenovo ThinkPad for programming",
        "Sony WH-1000XM5 wireless noise cancelling headphones"
    ]
    embs = embedder.encode_batch(batch)
    assert len(embs) == 2
    assert len(embs[0]) == 384
    assert len(embs[1]) == 384

def test_build_searchable_text():
    prod = {
        "name": "ASUS TUF Gaming A15",
        "brand": "ASUS",
        "category": "Laptops",
        "description": "High performance gaming laptop",
        "specifications": {"ram_gb": 16, "gpu": "RTX 4060"}
    }
    searchable = ProductEmbedder.build_searchable_text(prod)
    assert "ASUS TUF Gaming A15" in searchable
    assert "Brand: ASUS" in searchable
    assert "Category: Laptops" in searchable
    assert "Ram Gb: 16" in searchable
    assert "Gpu: RTX 4060" in searchable
