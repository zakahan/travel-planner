from abc import ABC, abstractmethod
from .vector import KnowledgeBaseVector
from .vector_type import VectorType

class AbstractVectorFactory(ABC):
    @abstractmethod
    def init_vector(self, collection_name: str) -> KnowledgeBaseVector:
        raise NotImplementedError
    


class VectorGenerator:
    @staticmethod
    def get_vector(vector_type: str, collection_name: str) -> KnowledgeBaseVector:
        match vector_type:
            case VectorType.ELASTICSEARCH:
                from .es_vector import ElasticSearchVectorFactory, ESVector
                factory = ElasticSearchVectorFactory()
                return factory.init_vector(collection_name=collection_name)
            case _:
                raise ValueError(f"Vector store {vector_type} is not supported now.")