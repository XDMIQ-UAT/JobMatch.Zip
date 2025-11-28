"""
Vector Database Setup Examples

Demonstrates how to set up and use different vector databases.
"""

import os
from src.tools.vector_db_storage import VectorDBStorageTool


def setup_chromadb():
    """Setup ChromaDB (local, easy setup)."""
    print("Setting up ChromaDB...")
    
    vector_db = VectorDBStorageTool(
        provider="chroma",
        connection_params={
            "persist_directory": "./chroma_db"  # Local storage directory
        }
    )
    
    print("✅ ChromaDB initialized")
    print("   - Storage: Local filesystem")
    print("   - Location: ./chroma_db/")
    print("   - No API keys required")
    
    return vector_db


def setup_pinecone():
    """Setup Pinecone (cloud, production-ready)."""
    print("Setting up Pinecone...")
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not set")
        print("   Get your API key at: https://www.pinecone.io/")
        return None
    
    vector_db = VectorDBStorageTool(
        provider="pinecone",
        connection_params={
            "api_key": api_key,
            "environment": os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp"),
            "index_name": os.getenv("PINECONE_INDEX_NAME", "jobmatch")
        }
    )
    
    print("✅ Pinecone initialized")
    print("   - Storage: Cloud (managed)")
    print("   - Environment: us-east1-gcp")
    print("   - Index: jobmatch")
    
    return vector_db


def setup_weaviate():
    """Setup Weaviate (self-hosted or cloud)."""
    print("Setting up Weaviate...")
    
    # Option 1: Local instance
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    
    vector_db = VectorDBStorageTool(
        provider="weaviate",
        connection_params={
            "url": weaviate_url
        }
    )
    
    print("✅ Weaviate initialized")
    print(f"   - URL: {weaviate_url}")
    print("   - Make sure Weaviate is running:")
    print("     docker run -p 8080:8080 semitechnologies/weaviate")
    
    return vector_db


def example_usage(vector_db):
    """Example of using vector DB storage."""
    print("\nExample: Storing job description...")
    
    try:
        result = vector_db.execute(
            content_type="job_description",
            source="https://example.com/job",
            analysis={
                "title": "Software Engineer",
                "required_skills": ["Python", "JavaScript"],
                "experience_level": "senior"
            },
            raw_content="Full job description text..."
        )
        
        print(f"✅ Stored with ID: {result['id']}")
        print(f"   Content type: {result['content_type']}")
        print(f"   Source: {result['source']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function demonstrating different setups."""
    print("=" * 80)
    print("Vector Database Setup Examples")
    print("=" * 80 + "\n")
    
    # Choose your vector DB
    choice = input("Choose vector DB (1=ChromaDB, 2=Pinecone, 3=Weaviate): ").strip()
    
    if choice == "1":
        vector_db = setup_chromadb()
    elif choice == "2":
        vector_db = setup_pinecone()
    elif choice == "3":
        vector_db = setup_weaviate()
    else:
        print("Invalid choice. Using ChromaDB by default.")
        vector_db = setup_chromadb()
    
    if vector_db:
        example_usage(vector_db)
    
    print("\n" + "=" * 80)
    print("For more information, see DATA_SOURCES_AND_VECTOR_DB.md")
    print("=" * 80)


if __name__ == "__main__":
    main()

