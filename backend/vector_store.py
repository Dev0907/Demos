from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from backend.config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL_NAME
import uuid

# Initialize Client
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Initialize Embedding Model
# Note: This might download the model on first run
encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)

COLLECTION_NAME = "edumind_docs"

def ensure_collection():
    try:
        client.get_collection(COLLECTION_NAME)
        # Try to create the index if it doesn't exist
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="pdf_path",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            print("Created pdf_path index")
        except Exception as e:
            # Index might already exist
            pass
    except Exception:
        # Create collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        # Create index for pdf_path
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="pdf_path",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print("Created collection with pdf_path index")

def add_documents(text_chunks: list[str], metadata: dict):
    ensure_collection()
    
    points = []
    for chunk in text_chunks:
        vector = encoder.encode(chunk).tolist()
        points.append(models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk, **metadata}
        ))
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search_documents(query: str, limit: int = 3, pdf_path: str = None):
    ensure_collection()
    query_vector = encoder.encode(query).tolist()
    
    # Build filter if pdf_path is provided
    query_filter = None
    if pdf_path:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="pdf_path",
                    match=models.MatchValue(value=pdf_path)
                )
            ]
        )
    
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=limit
    )
    
    return [hit.payload for hit in hits]
