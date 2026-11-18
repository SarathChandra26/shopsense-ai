import sqlite3
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.logging import logger

def init_fts_table(db: Session) -> None:
    """Initialize the SQLite FTS5 full-text search table for products."""
    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
            product_id UNINDEXED,
            name,
            brand,
            category,
            description,
            specifications_text,
            tokenize = 'porter unicode61'
        );
    """)
    raw_conn.commit()
    logger.info("SQLite FTS5 products_fts table initialized successfully.")

def index_product_fts(
    db: Session,
    product_id: str,
    name: str,
    brand: str,
    category: str,
    description: str,
    specifications_text: str = ""
) -> None:
    """Insert or replace a product document in the FTS5 table."""
    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    # Delete existing entry if present
    cursor.execute("DELETE FROM products_fts WHERE product_id = ?", (product_id,))
    cursor.execute(
        """
        INSERT INTO products_fts (product_id, name, brand, category, description, specifications_text)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (product_id, name, brand, category, description, specifications_text)
    )
    raw_conn.commit()

def delete_product_fts(db: Session, product_id: str) -> None:
    """Remove a product entry from the FTS5 index."""
    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    cursor.execute("DELETE FROM products_fts WHERE product_id = ?", (product_id,))
    raw_conn.commit()

def search_fts(db: Session, query: str, limit: int = 50) -> List[Tuple[str, float]]:
    """
    Search the FTS5 index using BM25 ranking.
    Returns list of tuples: (product_id, bm25_score)
    FTS5 'rank' is lower-is-better (usually negative), we normalize so higher is better.
    """
    if not query or not query.strip():
        return []

    # Clean query for FTS5 syntax
    # Tokenize words, escape special FTS characters
    words = [w.strip() for w in query.replace('"', ' ').replace("'", ' ').split() if len(w.strip()) > 1]
    if not words:
        return []

    # Format as an FTS MATCH expression: word1 OR word2 OR "word1 word2"
    safe_terms = " OR ".join([f'"{w}"*' for w in words])
    
    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    try:
        cursor.execute(
            """
            SELECT product_id, bm25(products_fts) as score
            FROM products_fts
            WHERE products_fts MATCH ?
            ORDER BY score ASC
            LIMIT ?
            """,
            (safe_terms, limit)
        )
        rows = cursor.fetchall()
        # Convert BM25 score to normalized positive range [0, 1]
        results = []
        for pid, score in rows:
            # score is negative in sqlite bm25 (e.g. -5.4); closer to 0 is less relevant, more negative is more relevant
            # abs(score) increases with relevance
            norm_score = abs(score) / (1.0 + abs(score))
            results.append((pid, float(norm_score)))
        return results
    except Exception as e:
        logger.warning(f"FTS search query failed for query '{query}': {e}")
        return []
