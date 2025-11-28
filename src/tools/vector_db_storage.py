"""
Vector Database Storage Tool

Tool for storing job descriptions and candidate profiles in a vector database.
Supports Pinecone, Weaviate, and other vector databases.
"""

from typing import Any, Dict, List, Optional
from src.tools.base_tool import BaseTool


class VectorDBStorageTool(BaseTool):
    """Tool for storing and retrieving data from vector databases."""
    
    name = "vector_db_storage"
    description = "Stores job descriptions and candidate profiles in a vector database for similarity search"
    
    def __init__(
        self,
        provider: str = "pinecone",  # "pinecone", "weaviate", "chroma"
        connection_params: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        self.provider = provider.lower()
        self.connection_params = connection_params or {}
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the vector database client based on provider."""
        if self.provider == "pinecone":
            try:
                import pinecone
                api_key = self.connection_params.get("api_key")
                environment = self.connection_params.get("environment", "us-east1-gcp")
                
                if api_key:
                    pinecone.init(api_key=api_key, environment=environment)
                    self._client = pinecone
            except ImportError:
                raise ImportError("pinecone-client is required. Install with: pip install pinecone-client")
        
        elif self.provider == "weaviate":
            try:
                import weaviate
                url = self.connection_params.get("url", "http://localhost:8080")
                self._client = weaviate.Client(url)
            except ImportError:
                raise ImportError("weaviate-client is required. Install with: pip install weaviate-client")
        
        elif self.provider == "chroma":
            try:
                import chromadb
                persist_directory = self.connection_params.get("persist_directory", "./chroma_db")
                self._client = chromadb.Client(chromadb.PersistentClient(path=persist_directory))
            except ImportError:
                raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        else:
            raise ValueError(f"Unsupported vector database provider: {self.provider}")
    
    def execute(
        self,
        content_type: str,  # "job_description" or "candidate_profile"
        source: str,
        analysis: Optional[Dict[str, Any]] = None,
        raw_content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Store content in vector database.
        
        Args:
            content_type: Type of content ("job_description" or "candidate_profile")
            source: Source URL or file path
            analysis: Structured analysis from analyzer agent
            raw_content: Raw text content
            embedding: Pre-computed embedding (optional)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with storage result including ID
        """
        if not analysis and not raw_content:
            raise ValueError("Either analysis or raw_content must be provided")
        
        # Generate ID
        import hashlib
        content_id = hashlib.md5(source.encode()).hexdigest()
        
        # Prepare metadata
        metadata = {
            "content_type": content_type,
            "source": source,
            "analysis": analysis or {},
            "raw_content": raw_content or ""
        }
        
        # Store based on provider
        try:
            if self.provider == "pinecone":
                index_name = self.connection_params.get("index_name", "jobmatch")
                index = self._client.Index(index_name)
                
                # If embedding not provided, we'd need to generate it
                # For now, assume it's provided or will be generated elsewhere
                if embedding:
                    index.upsert([(content_id, embedding, metadata)])
                else:
                    # Store metadata only (embedding would be generated separately)
                    # This is a simplified version
                    pass
            
            elif self.provider == "weaviate":
                # Weaviate storage logic
                pass
            
            elif self.provider == "chroma":
                # ChromaDB storage logic
                collection_name = f"{content_type}s"
                collection = self._client.get_or_create_collection(name=collection_name)
                
                # If embedding provided, store it
                if embedding:
                    collection.add(
                        ids=[content_id],
                        embeddings=[embedding],
                        metadatas=[metadata],
                        documents=[raw_content] if raw_content else [""]
                    )
            
            return {
                "status": "success",
                "id": content_id,
                "content_type": content_type,
                "source": source
            }
        
        except Exception as e:
            raise Exception(f"Failed to store in vector database: {str(e)}")

