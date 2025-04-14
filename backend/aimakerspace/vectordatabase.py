import numpy as np
from typing import List, Tuple
from aimakerspace.openai_utils.embedding import EmbeddingModel


class VectorDatabase:
    def __init__(self):
        print("Initializing VectorDatabase...")  # Debug log
        try:
            self.embedding_model = EmbeddingModel()
            print("EmbeddingModel initialized")  # Debug log
            self.embeddings = []
            self.texts = []
        except Exception as e:
            print(f"Error initializing VectorDatabase: {str(e)}")  # Debug log
            raise

    async def abuild_from_list(self, texts: List[str]):
        try:
            print(f"Building vector database from {len(texts)} texts")  # Debug log
            self.texts = texts
            print("Generating embeddings...")  # Debug log
            self.embeddings = await self.embedding_model.async_get_embeddings(texts)
            print(f"Generated {len(self.embeddings)} embeddings")  # Debug log
            return self
        except Exception as e:
            print(f"Error building vector database: {str(e)}")  # Debug log
            raise

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    async def search_by_text(self, query: str, k: int = 4) -> List[Tuple[str, float]]:
        try:
            print(f"Searching for query: {query}")  # Debug log
            query_embedding = await self.embedding_model.embed_query(query)
            print("Generated query embedding")  # Debug log
            
            # Calculate similarities
            similarities = []
            for i, embedding in enumerate(self.embeddings):
                similarity = self._cosine_similarity(query_embedding, embedding)
                similarities.append((self.texts[i], similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            print(f"Found {len(similarities)} matches")  # Debug log
            return similarities[:k]
        except Exception as e:
            print(f"Error in search_by_text: {str(e)}")  # Debug log
            raise 