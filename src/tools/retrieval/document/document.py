from pydantic import BaseModel
from typing import Optional


class Document(BaseModel):
    page_content: str
    vector: Optional[list[float]] = None
    metadata: dict = {}
    """
    metadata 
        source: Name of the source file
        vector_text: Vectorized text (i.e., this part of the code is processed into a vector. For unstructured text, the content of this field remains the same as that of page_content)
    """