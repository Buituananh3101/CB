import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from config import settings
import uuid

class VectorStore:
    def __init__(self):
        """Khởi tạo ChromaDB vector store"""
        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_STORE_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Tạo collection cho documents
        try:
            self.collection = self.client.get_collection("math_documents")
        except:
            self.collection = self.client.create_collection(
                name="math_documents",
                metadata={"hnsw:space": "cosine"}
            )
        
        # Configure Gemini for embeddings
        genai.configure(api_key=settings.GEMINI_API_KEY)
    
    def get_embedding(self, text: str) -> List[float]:
        """Tạo embedding vector cho text sử dụng Gemini"""
        try:
            # Gemini embedding model
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Lỗi tạo embedding: {str(e)}")
            # Fallback: tạo embedding đơn giản
            return [0.0] * 768
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any], chunks: List[str]):
        """Thêm document vào vector store"""
        try:
            chunk_ids = []
            chunk_embeddings = []
            chunk_texts = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk)
                
                # Tạo embedding cho chunk
                embedding = self.get_embedding(chunk)
                chunk_embeddings.append(embedding)
                
                # Metadata cho chunk
                chunk_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "doc_id": doc_id
                }
                chunk_metadatas.append(chunk_metadata)
            
            # Thêm vào collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                documents=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            return True
        except Exception as e:
            print(f"Lỗi thêm document vào vector store: {str(e)}")
            return False
    
    def search(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm documents liên quan đến query"""
        try:
            # Tạo embedding cho query
            query_embedding = self.get_embedding(query)
            
            # Tìm kiếm
            where_filter = None
            if document_ids:
                where_filter = {"doc_id": {"$in": document_ids}}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format kết quả
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Lỗi tìm kiếm: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str):
        """Xóa document khỏi vector store"""
        try:
            # Tìm tất cả chunks của document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return True
            return False
        except Exception as e:
            print(f"Lỗi xóa document: {str(e)}")
            return False
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả documents"""
        try:
            results = self.collection.get()
            
            # Group by doc_id
            docs = {}
            if results['metadatas']:
                for metadata in results['metadatas']:
                    doc_id = metadata.get('doc_id')
                    if doc_id and doc_id not in docs:
                        docs[doc_id] = {
                            "id": doc_id,
                            "filename": metadata.get('filename', 'Unknown'),
                            "file_type": metadata.get('file_type', 'Unknown')
                        }
            
            return list(docs.values())
        except Exception as e:
            print(f"Lỗi lấy danh sách documents: {str(e)}")
            return []
