from typing import Any

from elasticsearch import Elasticsearch
import os
from pydantic import BaseModel
from urllib.parse import urlparse
import requests
from tools.config import tools_cfg as cfg
from tools.retrieval.document import Document
from tools.retrieval.vkb.vector import KnowledgeBaseVector
from tools.retrieval.vkb.vector_factory import AbstractVectorFactory


class ElasticSearchConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def validate_config(cls, values: dict) -> dict:
        if not values["host"]:
            raise ValueError("config HOST is required")
        if not values["port"]:
            raise ValueError("config PORT is required")
        if not values["username"]:
            raise ValueError("config USERNAME is required")
        if not values["password"]:
            raise ValueError("config PASSWORD is required")
        return values


class ESVector(KnowledgeBaseVector):

    def __init__(self, collection_name: str, config: Any):
        super().__init__(collection_name)
        self._client = self._init_client(config)



    def _init_client(self, config: ElasticSearchConfig) -> Elasticsearch:
        try:
            parsed_url = urlparse(config.host)
            if parsed_url.scheme in {"http", "https"}:
                hosts = f"{config.host}:{config.port}"
            else:
                hosts = f"http://{config.host}:{config.port}"
            client = Elasticsearch(
                hosts=hosts,
                basic_auth=(config.username, config.password),
                request_timeout=100,
                retry_on_timeout=True,
                max_retries=100,
                ssl_show_warn=False,  # Disable SSL warnings
                verify_certs=False    # Disable certificate verification
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Vector database connection error")

        return client
    def create(self, texts: list[Document], **kwargs):
        if texts[0].vector is not None:
            dim = len(texts[0].vector)
        else:
            dim = kwargs.get('dim', 1024)   # default as 1024
            pass
        self.create_collection(embedding_dim=dim)
        self.add_texts(texts, **kwargs)
        return

    def create_collection(
            self,
            embedding_dim: int, 
    ):
        # 我们的应用情景不需要考虑并发冲突问题
        if not self._client.indices.exists(index=self._collection_name):
            self._client.indices.create(
                index=self._collection_name, 
                mappings=self.default_mappings(dim=embedding_dim),
                settings=self.default_settings())
            
            pass
        return 
    

    def add_texts(self, documents: list[Document], **kwargs) -> None:
        # 考虑结构化的添加
        for i in range(len(documents)):
            self._client.index(
                index = self._collection_name,
                document={
                    "page_content": documents[i].page_content,
                    "vector": documents[i].vector,
                    "metadata": documents[i].metadata 
                }
            )
            pass
        self._client.indices.refresh(index=self._collection_name)
        return 


    def default_settings(self) -> dict:
        # 获取setting
        settings = {
            'index': {
                'number_of_shards': 1,  
                'number_of_replicas': 0, 
                'similarity': {
                    'custom_bm25': {
                        'type': 'BM25',
                        'k1': 1.2,
                        'b': 0.75
                    }
                }
            }  # end-of-index
        }
        return settings

    def default_mappings(self, dim: int = 1024) -> dict:
        mappings = {
            "properties": {
                "text": {
                    "type": "text",
                    "similarity": "custom_bm25",  # use custom bm25 function
                    "index": True,
                    "analyzer": "standard",
                    "search_analyzer": "standard"
                },
                
                "vector": {
                    "type": "dense_vector",  
                    "dims": dim,  
                    "index": True,  
                    "similarity": "l2_norm"  
                },

                "metadata": {
                    "type": "object",
                    "properties":{
                        "source": {"type": "keyword"},
                        "vector_text": {"type": "keyword"}  
                    }
                }
            }
        }
        return mappings
        

    def collection_exist(self) -> bool:
        from elasticsearch import BadRequestError
        try:
            return self._client.indices.exists(index=self._collection_name)
        except BadRequestError as e:
            print(f"BadRequestError: {e}")
            if hasattr(e, 'body') and e.body:
                print(f"Error details: {e.body}")
            return False
        
    def delete(self) -> None:
        self._client.indices.delete(index=self._collection_name)
        return
    
    def search_by_full_text(self, query: str, **kwargs: Any) -> list[Document]:
        pass
    
    def search_by_vector(self, query_vector: list[float], **kwargs: Any) -> list[Document]:
        top_k = kwargs.get('top_k', 10)
        num_candidates = kwargs.get('num_candidates', 2*top_k)
        query_body = {
            "knn":  {
                "field": "vector",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": num_candidates
            },
            "fields":[
                'vector',
                'page_content'
            ]

        }
        response = self._client.search(index=self._collection_name, body=query_body)
        result_list = []
        for hit in response['hits']['hits']:
            m_data = hit['_source']['metadata']
            m_data['score'] = hit['_score']
            result_list.append(
                Document(
                    page_content=hit['_source']['page_content'],
                    vector=hit['_source']['vector'],
                    metadata=m_data
                )    
            )

        return result_list
        
        pass
    def search_by_keyword(self, query: str, **kwargs: Any) -> list[Document]:
        pass    

    def get_health(self):
        response = self._client.cat.health(v=True)
        print(response)




class ElasticSearchVectorFactory(AbstractVectorFactory):
    def init_vector(self, collection_name:str) -> ESVector:
        return ESVector(
            collection_name=collection_name,
            config=ElasticSearchConfig(
                host=cfg['elastic'].get("ELASTICSEARCH_HOST", "localhost"),
                port=cfg['elastic'].get("ELASTICSEARCH_PORT", 9200),
                username=cfg['elastic'].get("ELASTICSEARCH_USERNAME", ""),
                password=cfg['elastic'].get("ELASTICSEARCH_PASSWORD", ""),
            )
        )