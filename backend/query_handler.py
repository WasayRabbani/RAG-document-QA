"""
Hybrid Search + Reranking Query Handler.

Search Strategy:
1. HyDE: Generate a hypothetical answer via Groq
2. Semantic Search (FAISS): Embed the HyDE answer, find top 20 similar chunks
3. Keyword Search (BM25): Find top 20 chunks by exact keyword matching
4. Merge: Combine results from both (deduplicated)
5. Rerank: CrossEncoder scores all candidates against the ORIGINAL question
6. Return: Top 3 most relevant chunks
"""

import os
import numpy as np
import faiss
import logging
from openai import OpenAI
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from local_embedder import get_embedder

load_dotenv()
logger = logging.getLogger(__name__)

class QueryHandler:
    def __init__(self, question, container, chunks, client=None, threshold=1.5):
        self.query = question
        self.container = container
        self.client = client
        self.chunks = chunks
        self.threshold = threshold
        self.embedder = get_embedder()

    def _generate_hypothetical_answer(self) -> str:
        """HyDE: Generate a fake answer to improve semantic search."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self.query

            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a technical document expert. Given a question, write a short 2-3 sentence passage that would directly answer it. Write it as if you are quoting from the source document. Do not say 'I don't know'. Just write a plausible answer."},
                    {"role": "user", "content": self.query}
                ],
                temperature=0,
                max_tokens=150
            )
            
            hypothetical = response.choices[0].message.content
            logger.info(f"HyDE generated: {hypothetical[:80]}...")
            return hypothetical
            
        except Exception as e:
            logger.warning(f"HyDE failed, using raw question: {e}")
            return self.query

    def _semantic_search(self, hyde_text: str) -> list:
        """FAISS semantic search using the HyDE embedding."""
        embedded = self.embedder.encode(hyde_text)
        query_array = np.array([embedded], dtype=np.float32)
        
        k = min(20, len(self.chunks))  # Don't request more than we have
        distances, indices = self.container.search(query_array, k=k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks) and dist < self.threshold:
                results.append((idx, self.chunks[idx]))
        
        return results

    def _bm25_search(self) -> list:
        """BM25 keyword search using the original question."""
        # Tokenize all chunks for BM25
        tokenized_chunks = [chunk['text'].lower().split() for chunk in self.chunks]
        bm25 = BM25Okapi(tokenized_chunks)
        
        # Tokenize the query
        tokenized_query = self.query.lower().split()
        
        # Get BM25 scores for all chunks
        scores = bm25.get_scores(tokenized_query)
        
        # Get top 20 by BM25 score
        top_indices = np.argsort(scores)[::-1][:20]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include chunks with some keyword match
                results.append((int(idx), self.chunks[idx]))
        
        return results

    def get_results(self):
        # Step 1: HyDE
        hyde_text = self._generate_hypothetical_answer()
        
        # Step 2: Semantic search (FAISS)
        semantic_results = self._semantic_search(hyde_text)
        logger.info(f"Semantic search returned {len(semantic_results)} candidates")
        
        # Step 3: Keyword search (BM25)
        bm25_results = self._bm25_search()
        logger.info(f"BM25 search returned {len(bm25_results)} candidates")
        
        # Step 4: Merge and deduplicate
        seen_indices = set()
        candidate_chunks = []
        
        for idx, chunk in semantic_results + bm25_results:
            if idx not in seen_indices:
                seen_indices.add(idx)
                candidate_chunks.append(chunk)
        
        logger.info(f"Merged: {len(candidate_chunks)} unique candidates")
        
        if not candidate_chunks:
            return []

        # Step 5: Rerank ALL candidates with CrossEncoder (using ORIGINAL question)
        from local_reranker import get_reranker
        reranker = get_reranker()
        
        pairs = [[self.query, chunk['text']] for chunk in candidate_chunks]
        scores = reranker.predict(pairs)
        
        for i, chunk in enumerate(candidate_chunks):
            chunk['rerank_score'] = float(scores[i])
        
        candidate_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Log top 5 for debugging
        for chunk in candidate_chunks[:5]:
            logger.info(f"  Page {chunk['page']} score: {chunk['rerank_score']:.2f}")
        
        # Step 6: Return top 3
        return candidate_chunks[:3]
