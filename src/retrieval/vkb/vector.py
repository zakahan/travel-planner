
from abc import ABC, abstractmethod
from ..document import Document
from typing import Any

class KnowledgeBaseVector(ABC):
    def __init__(
            self, 
            collection_name: str
    ):
        self._collection_name = collection_name

    @abstractmethod
    def create(self, texts: list[Document], **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add_texts(self, documents: list[Document], **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def collection_exist(self) -> bool:
        raise NotImplementedError

    @property
    def collection_name(self):
        return self._collection_name
    
    @abstractmethod
    def search_by_full_text(self, query: str, **kwargs: Any)-> list[Document]:
        raise NotImplementedError
    
    @abstractmethod
    def search_by_vector(self, query_vector: list[float], **kwagrs: Any) -> list[Document]:
        raise NotImplementedError
    
    @abstractmethod
    def search_by_keyword(self, query: str, **kwargs: Any)-> list[Document]:
        raise NotImplementedError
    


