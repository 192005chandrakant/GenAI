"""
FAISS Service for similarity search and caching.
Provides efficient similarity search for claims and content.
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pickle
import os

import numpy as np
import faiss
from google.cloud import firestore

from app.core.config import settings
from app.models.schemas import CheckAnalysis, Language

logger = logging.getLogger(__name__)


class FAISSService:
    """Service for FAISS similarity search and caching."""
    
    def __init__(self):
        """Initialize FAISS service."""
        self.index_path = settings.FAISS_INDEX_PATH
        self.dimension = settings.FAISS_DIMENSION
        self.nprobe = settings.FAISS_NPROBE
        self.use_mock = settings.USE_MOCKS
        
        # Initialize FAISS index
        self.index = None
        self.claim_ids = []
        self.claim_embeddings = []
        
        # Firestore client for metadata
        try:
            if not self.use_mock:
                self.db = firestore.Client()
                logger.info("FAISS Service initialized with Firestore")
            else:
                print("🔄 Using mock FAISS service (USE_MOCKS=True)")
                self.db = None
                
        except Exception as e:
            print(f"Failed to initialize Firestore for FAISS: {str(e)}")
            print("🔄 Falling back to mock FAISS service")
            self.use_mock = True
            self.db = None
        
        logger.info("FAISS Service initialized")
    
    async def initialize_index(self):
        """Initialize or load FAISS index."""
        try:
            if os.path.exists(self.index_path):
                await self._load_index()
            else:
                await self._create_index()
            
            logger.info(f"FAISS index initialized with {len(self.claim_ids)} claims")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {str(e)}")
            await self._create_index()
    
    async def add_claim(
        self, 
        claim_id: str, 
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """
        Add a claim to the FAISS index.
        
        Args:
            claim_id: Unique claim identifier
            embedding: Claim embedding vector
            metadata: Additional claim metadata
        """
        try:
            # Convert embedding to numpy array
            embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
            
            # Add to FAISS index
            if self.index is None:
                await self.initialize_index()
            
            self.index.add(embedding_array)
            
            # Store metadata
            self.claim_ids.append(claim_id)
            self.claim_embeddings.append(embedding)
            
            # Save metadata to Firestore
            await self._save_claim_metadata(claim_id, metadata)
            
            logger.info(f"Added claim {claim_id} to FAISS index")
            
        except Exception as e:
            logger.error(f"Error adding claim to FAISS index: {str(e)}")
            raise
    
    async def search_similar_claims(
        self, 
        query_embedding: List[float],
        k: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar claims using FAISS.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of similar claims with metadata
        """
        if self.use_mock:
            # Return mock similar claims for development
            return [
                {
                    "claim_id": "mock_claim_1",
                    "similarity": 0.85,
                    "claim_text": "Mock similar claim for development",
                    "source": "Mock Source",
                    "date": datetime.utcnow().isoformat()
                },
                {
                    "claim_id": "mock_claim_2", 
                    "similarity": 0.75,
                    "claim_text": "Another mock claim for testing",
                    "source": "Mock Source 2",
                    "date": datetime.utcnow().isoformat()
                }
            ]
        
        try:
            if self.index is None:
                await self.initialize_index()
            
            # Convert query to numpy array
            query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
            
            # Search FAISS index
            distances, indices = self.index.search(query_array, min(k, len(self.claim_ids)))
            
            # Get results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.claim_ids):
                    claim_id = self.claim_ids[idx]
                    
                    # Convert distance to similarity score
                    similarity = 1.0 - distance
                    
                    if similarity >= threshold:
                        # Get metadata from Firestore
                        metadata = await self._get_claim_metadata(claim_id)
                        
                        results.append({
                            "claim_id": claim_id,
                            "similarity": float(similarity),
                            "distance": float(distance),
                            "metadata": metadata
                        })
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar claims: {str(e)}")
            return []
    
    async def batch_add_claims(
        self, 
        claims: List[Tuple[str, List[float], Dict[str, Any]]]
    ):
        """
        Add multiple claims to the FAISS index in batch.
        
        Args:
            claims: List of (claim_id, embedding, metadata) tuples
        """
        try:
            if not claims:
                return
            
            # Prepare embeddings
            embeddings = []
            claim_ids = []
            metadatas = []
            
            for claim_id, embedding, metadata in claims:
                embeddings.append(embedding)
                claim_ids.append(claim_id)
                metadatas.append(metadata)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Add to FAISS index
            if self.index is None:
                await self.initialize_index()
            
            self.index.add(embeddings_array)
            
            # Update local storage
            self.claim_ids.extend(claim_ids)
            self.claim_embeddings.extend(embeddings)
            
            # Save metadata to Firestore in batch
            await self._batch_save_claim_metadata(claim_ids, metadatas)
            
            logger.info(f"Added {len(claims)} claims to FAISS index in batch")
            
        except Exception as e:
            logger.error(f"Error batch adding claims: {str(e)}")
            raise
    
    async def update_claim(
        self, 
        claim_id: str, 
        new_embedding: List[float],
        new_metadata: Dict[str, Any]
    ):
        """
        Update an existing claim in the FAISS index.
        
        Args:
            claim_id: Claim identifier
            new_embedding: New embedding vector
            new_metadata: Updated metadata
        """
        try:
            if claim_id not in self.claim_ids:
                raise ValueError(f"Claim {claim_id} not found in index")
            
            # Find claim index
            claim_idx = self.claim_ids.index(claim_id)
            
            # Update embedding
            new_embedding_array = np.array(new_embedding, dtype=np.float32).reshape(1, -1)
            
            # Remove old embedding and add new one
            # Note: FAISS doesn't support direct updates, so we need to rebuild
            await self._rebuild_index_with_update(claim_idx, new_embedding_array)
            
            # Update local storage
            self.claim_embeddings[claim_idx] = new_embedding
            
            # Update metadata in Firestore
            await self._save_claim_metadata(claim_id, new_metadata)
            
            logger.info(f"Updated claim {claim_id} in FAISS index")
            
        except Exception as e:
            logger.error(f"Error updating claim: {str(e)}")
            raise
    
    async def remove_claim(self, claim_id: str):
        """
        Remove a claim from the FAISS index.
        
        Args:
            claim_id: Claim identifier to remove
        """
        try:
            if claim_id not in self.claim_ids:
                logger.warning(f"Claim {claim_id} not found in index")
                return
            
            # Find claim index
            claim_idx = self.claim_ids.index(claim_id)
            
            # Remove from FAISS index (rebuild without this claim)
            await self._rebuild_index_without_claim(claim_idx)
            
            # Remove from local storage
            self.claim_ids.pop(claim_idx)
            self.claim_embeddings.pop(claim_idx)
            
            # Remove metadata from Firestore
            await self._remove_claim_metadata(claim_id)
            
            logger.info(f"Removed claim {claim_id} from FAISS index")
            
        except Exception as e:
            logger.error(f"Error removing claim: {str(e)}")
            raise
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get FAISS index statistics."""
        try:
            if self.index is None:
                return {"total_claims": 0, "index_size": 0}
            
            return {
                "total_claims": len(self.claim_ids),
                "index_size": self.index.ntotal,
                "dimension": self.dimension,
                "nprobe": self.nprobe
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"total_claims": 0, "index_size": 0}
    
    async def save_index(self):
        """Save FAISS index to disk."""
        try:
            if self.index is None:
                return
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata_path = f"{self.index_path}_metadata.pkl"
            metadata = {
                "claim_ids": self.claim_ids,
                "claim_embeddings": self.claim_embeddings,
                "timestamp": datetime.utcnow()
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info("FAISS index saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _create_index(self):
        """Create a new FAISS index."""
        try:
            # Create IVF index with PCA
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)  # 100 clusters
            
            # Set search parameters
            self.index.nprobe = self.nprobe
            
            logger.info("Created new FAISS index")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise
    
    async def _load_index(self):
        """Load existing FAISS index from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            metadata_path = f"{self.index_path}_metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                self.claim_ids = metadata.get("claim_ids", [])
                self.claim_embeddings = metadata.get("claim_embeddings", [])
            
            logger.info("Loaded existing FAISS index")
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            await self._create_index()
    
    async def _rebuild_index_with_update(self, claim_idx: int, new_embedding: np.ndarray):
        """Rebuild index with updated claim."""
        try:
            # Create new embeddings array
            new_embeddings = []
            for i, embedding in enumerate(self.claim_embeddings):
                if i == claim_idx:
                    new_embeddings.append(new_embedding[0])
                else:
                    new_embeddings.append(embedding)
            
            # Rebuild index
            await self._rebuild_index(new_embeddings)
            
        except Exception as e:
            logger.error(f"Error rebuilding index with update: {str(e)}")
            raise
    
    async def _rebuild_index_without_claim(self, claim_idx: int):
        """Rebuild index without specified claim."""
        try:
            # Create new embeddings array without the claim
            new_embeddings = [
                embedding for i, embedding in enumerate(self.claim_embeddings)
                if i != claim_idx
            ]
            
            # Rebuild index
            await self._rebuild_index(new_embeddings)
            
        except Exception as e:
            logger.error(f"Error rebuilding index without claim: {str(e)}")
            raise
    
    async def _rebuild_index(self, embeddings: List[List[float]]):
        """Rebuild FAISS index with new embeddings."""
        try:
            if not embeddings:
                await self._create_index()
                return
            
            # Create new index
            await self._create_index()
            
            # Add embeddings
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.train(embeddings_array)
            self.index.add(embeddings_array)
            
            logger.info("Rebuilt FAISS index")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {str(e)}")
            raise
    
    async def _save_claim_metadata(self, claim_id: str, metadata: Dict[str, Any]):
        """Save claim metadata to Firestore."""
        try:
            doc_ref = self.db.collection('faiss_metadata').document(claim_id)
            doc_ref.set({
                **metadata,
                'updated_at': datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error saving claim metadata: {str(e)}")
    
    async def _batch_save_claim_metadata(
        self, 
        claim_ids: List[str], 
        metadatas: List[Dict[str, Any]]
    ):
        """Save multiple claim metadata to Firestore in batch."""
        try:
            batch = self.db.batch()
            
            for claim_id, metadata in zip(claim_ids, metadatas):
                doc_ref = self.db.collection('faiss_metadata').document(claim_id)
                batch.set(doc_ref, {
                    **metadata,
                    'updated_at': datetime.utcnow()
                })
            
            batch.commit()
            
        except Exception as e:
            logger.error(f"Error batch saving claim metadata: {str(e)}")
    
    async def _get_claim_metadata(self, claim_id: str) -> Dict[str, Any]:
        """Get claim metadata from Firestore."""
        try:
            doc_ref = self.db.collection('faiss_metadata').document(claim_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return {}
            
        except Exception as e:
            logger.error(f"Error getting claim metadata: {str(e)}")
            return {}
    
    async def _remove_claim_metadata(self, claim_id: str):
        """Remove claim metadata from Firestore."""
        try:
            doc_ref = self.db.collection('faiss_metadata').document(claim_id)
            doc_ref.delete()
            
        except Exception as e:
            logger.error(f"Error removing claim metadata: {str(e)}")


# Create a singleton instance
faiss_service = FAISSService()
