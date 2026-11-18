import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger

_CHROMA_CLIENT: Optional[chromadb.PersistentClient] = None

class ChromaVectorStore:
    def __init__(self, persist_dir: str = str(settings.CHROMA_PATH)):
        self.persist_dir = persist_dir
        logger.info(f"Connecting to persistent ChromaDB at: {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        # Use cosine similarity space
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB collection '{self.collection_name}' ready. Current count: {self.collection.count()}")

    def upsert_products_batch(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Upsert a batch of product vectors into ChromaDB."""
        if not ids:
            return

        # Deduplicate records by ID within the batch (keep latest)
        seen_ids = set()
        dedup_ids = []
        dedup_embs = []
        dedup_docs = []
        dedup_metas = []
        
        # Traverse in reverse to keep latest
        for i in range(len(ids) - 1, -1, -1):
            pid = ids[i]
            if pid not in seen_ids:
                seen_ids.add(pid)
                dedup_ids.append(pid)
                dedup_embs.append(embeddings[i])
                dedup_docs.append(documents[i])
                dedup_metas.append(metadatas[i])
                
        dedup_ids.reverse()
        dedup_embs.reverse()
        dedup_docs.reverse()
        dedup_metas.reverse()

        # ChromaDB requires metadata values to be str, int, float, bool
        sanitized_metadatas = []
        for meta in dedup_metas:
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                elif v is None:
                    clean_meta[k] = ""
                else:
                    clean_meta[k] = str(v)
            sanitized_metadatas.append(clean_meta)

        self.collection.upsert(
            ids=dedup_ids,
            embeddings=dedup_embs,
            documents=dedup_docs,
            metadatas=sanitized_metadatas
        )

    def upsert_product(
        self,
        product_id: str,
        embedding: List[float],
        document: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Incrementally index or update a single product vector without rebuilding the index."""
        self.upsert_products_batch([product_id], [embedding], [document], [metadata])

    def delete_product(self, product_id: str) -> None:
        """Remove a product vector from the collection."""
        try:
            self.collection.delete(ids=[product_id])
            logger.info(f"Deleted vector for product {product_id} from ChromaDB.")
        except Exception as e:
            logger.warning(f"Failed to delete vector for product {product_id}: {e}")

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 20,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Query nearest neighbors by cosine similarity.
        Returns list of (product_id, similarity_score, metadata)
        Cosine distance in ChromaDB is in [0, 2], where 0 is identical.
        Similarity score = 1.0 - (distance / 2.0) or max(0, 1.0 - distance)
        """
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)
        
        output = []
        if results and "ids" in results and results["ids"]:
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(ids)
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(ids)

            for pid, dist, meta in zip(ids, distances, metas):
                # Cosine similarity: 1.0 - distance
                sim = max(0.0, min(1.0, 1.0 - dist))
                output.append((pid, float(sim), meta))
        return output

    def get_count(self) -> int:
        return self.collection.count()

    def check_consistency(self, db_product_ids: List[str]) -> Dict[str, Any]:
        """Verify vector index consistency against SQL database IDs."""
        total_chroma = self.collection.count()
        total_sql = len(db_product_ids)
        
        # Sample or check if sizes match
        return {
            "chroma_count": total_chroma,
            "sql_count": total_sql,
            "is_consistent": total_chroma == total_sql,
            "difference": total_sql - total_chroma
        }

_STORE_INSTANCE: Optional[ChromaVectorStore] = None

def get_vector_store() -> ChromaVectorStore:
    global _STORE_INSTANCE
    if _STORE_INSTANCE is None:
        _STORE_INSTANCE = ChromaVectorStore()
    return _STORE_INSTANCE
