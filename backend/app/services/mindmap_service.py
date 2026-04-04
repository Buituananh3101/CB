import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import MindMapNode
from app.services.vector_store import VectorStore
import json
import uuid

class MindMapService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vector_store = VectorStore()
    
    async def generate_mindmap(
        self, 
        topic: str, 
        document_ids: Optional[List[str]] = None,
        depth: int = 3
    ) -> MindMapNode:
        """Tạo mind map cho chủ đề"""
        
        # Lấy context từ documents
        context = ""
        if document_ids:
            relevant_docs = self.vector_store.search(
                query=topic,
                document_ids=document_ids,
                top_k=5
            )
            if relevant_docs:
                context = "Thông tin từ tài liệu:\n"
                for doc in relevant_docs:
                    context += f"{doc['content'][:500]}\n\n"
        
        prompt = f"""
        Tạo một mind map chi tiết cho chủ đề toán học: {topic}
        
        {context}
        
        Yêu cầu:
        - Tạo cấu trúc phân cấp với tối đa {depth} cấp độ
        - Mỗi nhánh là một khái niệm/chủ đề con
        - Sắp xếp logic từ tổng quát đến chi tiết
        - Phù hợp với chương trình toán lớp 10-12
        
        Trả về dưới dạng JSON với cấu trúc:
        {{
            "text": "Tên nút chính",
            "children": [
                {{
                    "text": "Nút con 1",
                    "children": [...]
                }},
                {{
                    "text": "Nút con 2",
                    "children": [...]
                }}
            ]
        }}
        
        CHỈ TRẢ VỀ JSON, KHÔNG CÓ TEXT GIẢI THÍCH THÊM.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Làm sạch response để lấy JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            mindmap_data = json.loads(response_text)
            
            # Convert to MindMapNode
            return self._dict_to_mindmap_node(mindmap_data, level=0)
            
        except json.JSONDecodeError as e:
            # Fallback: tạo mind map đơn giản
            return self._create_fallback_mindmap(topic)
        except Exception as e:
            print(f"Lỗi tạo mind map: {str(e)}")
            return self._create_fallback_mindmap(topic)
    
    def _dict_to_mindmap_node(self, data: Dict[str, Any], level: int = 0) -> MindMapNode:
        """Chuyển dict sang MindMapNode"""
        node_id = str(uuid.uuid4())
        
        children = []
        if "children" in data and data["children"]:
            for child_data in data["children"]:
                child_node = self._dict_to_mindmap_node(child_data, level + 1)
                children.append(child_node)
        
        # Màu sắc theo level
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
        color = colors[level % len(colors)]
        
        return MindMapNode(
            id=node_id,
            text=data.get("text", ""),
            children=children,
            level=level,
            color=color
        )
    
    def _create_fallback_mindmap(self, topic: str) -> MindMapNode:
        """Tạo mind map mặc định khi có lỗi"""
        return MindMapNode(
            id=str(uuid.uuid4()),
            text=topic,
            children=[
                MindMapNode(
                    id=str(uuid.uuid4()),
                    text="Định nghĩa",
                    children=[],
                    level=1,
                    color="#4ECDC4"
                ),
                MindMapNode(
                    id=str(uuid.uuid4()),
                    text="Công thức",
                    children=[],
                    level=1,
                    color="#45B7D1"
                ),
                MindMapNode(
                    id=str(uuid.uuid4()),
                    text="Ví dụ",
                    children=[],
                    level=1,
                    color="#FFA07A"
                ),
                MindMapNode(
                    id=str(uuid.uuid4()),
                    text="Ứng dụng",
                    children=[],
                    level=1,
                    color="#98D8C8"
                )
            ],
            level=0,
            color="#FF6B6B"
        )
    
    async def generate_concept_map(
        self, 
        concepts: List[str], 
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Tạo concept map liên kết các khái niệm"""
        
        context = ""
        if document_ids:
            all_concepts = " ".join(concepts)
            relevant_docs = self.vector_store.search(
                query=all_concepts,
                document_ids=document_ids,
                top_k=3
            )
            if relevant_docs:
                context = "Thông tin:\n"
                for doc in relevant_docs:
                    context += f"{doc['content'][:300]}\n"
        
        prompt = f"""
        Tạo concept map (sơ đồ khái niệm) liên kết các khái niệm toán học sau:
        {", ".join(concepts)}
        
        {context}
        
        Trả về JSON với:
        - nodes: danh sách các nút (concepts)
        - edges: danh sách các cạnh liên kết (relationships)
        
        Format:
        {{
            "nodes": [
                {{"id": "1", "label": "Khái niệm A"}},
                {{"id": "2", "label": "Khái niệm B"}}
            ],
            "edges": [
                {{"from": "1", "to": "2", "label": "dẫn đến"}}
            ]
        }}
        
        CHỈ TRẢ VỀ JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except Exception as e:
            # Fallback
            return {
                "nodes": [{"id": str(i), "label": c} for i, c in enumerate(concepts)],
                "edges": []
            }
