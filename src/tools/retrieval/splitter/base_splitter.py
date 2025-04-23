from abc import ABC, abstractmethod
from tools.retrieval.document import Document
from typing import IO, Any


class Splitter(ABC):
    
    @abstractmethod
    def split_text(self, text: str, **kwargs: Any) -> list[Document]:
        """Split text into multiple components."""
        raise NotImplementedError
    
    @abstractmethod
    def split_file(self, file: IO, **kwargs: Any) -> list[Document]:
        """Split file into multiple components."""
        raise NotImplementedError
    
    @abstractmethod
    def split_documents(self, documents: list[Document],**kwargs: Any)-> list[Document]:
        """Split documents into multiple components."""
        raise NotImplementedError
    

