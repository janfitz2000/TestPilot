from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

from .config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for instrument documentation and knowledge base"""
    
    def __init__(self):
        self.client = None
        self.encoder = None
        self.collection_name = "instrument_docs"
        self.vector_size = 384  # all-MiniLM-L6-v2 embedding size
    
    async def initialize(self):
        """Initialize vector store connection and embedding model"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(url=settings.vector_store_url)
            
            # Initialize sentence transformer
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collection if it doesn't exist
            try:
                self.client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists")
            except Exception:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection_name}'")
                
                # Load initial documents
                await self._load_initial_documents()
            
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Fall back to mock implementation
            self.client = None
            self.encoder = None
    
    async def search_similar(self, query: str, limit: int = 5) -> List[str]:
        """Search for similar documents"""
        if not self.client or not self.encoder:
            # Return mock results for development
            return [
                "Mock instrument manual excerpt 1",
                "Mock instrument manual excerpt 2",
                "Mock test procedure example"
            ]
        
        try:
            # Encode query
            query_vector = self.encoder.encode(query).tolist()
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # Extract texts from results
            results = []
            for result in search_results:
                if result.payload and 'text' in result.payload:
                    results.append(result.payload['text'])
            
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add document to vector store"""
        if not self.client or not self.encoder:
            logger.warning("Vector store not available, skipping document addition")
            return
        
        try:
            # Encode text
            vector = self.encoder.encode(text).tolist()
            
            # Prepare payload
            payload = {'text': text}
            if metadata:
                payload.update(metadata)
            
            # Add to Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info("Document added to vector store")
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
    
    async def _load_initial_documents(self):
        """Load initial instrument documentation"""
        initial_docs = [
            {
                "text": "Oscilloscope SCPI Commands: :ACQuire:TYPE sets acquisition type. :MEASure:VPP measures peak-to-peak voltage.",
                "metadata": {"type": "scpi_command", "instrument": "oscilloscope"}
            },
            {
                "text": "Signal Generator Setup: Configure frequency using :SOURce:FREQuency command. Set amplitude with :SOURce:VOLTage:AMPLitude.",
                "metadata": {"type": "scpi_command", "instrument": "signal_generator"}
            },
            {
                "text": "SMU Measurement: Source-Measure Unit can source voltage and measure current simultaneously. Use :SOURce:VOLTage and :MEASure:CURRent commands.",
                "metadata": {"type": "scpi_command", "instrument": "smu"}
            },
            {
                "text": "Test Procedure Best Practices: Always initialize instruments before measurement. Set appropriate ranges and coupling. Allow settling time between commands.",
                "metadata": {"type": "best_practice", "category": "measurement"}
            }
        ]
        
        for doc in initial_docs:
            await self.add_document(doc["text"], doc["metadata"])
        
        logger.info(f"Loaded {len(initial_docs)} initial documents")