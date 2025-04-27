import os
import requests
import json
from .base_embedding import Embeddings


class ArkEmbeddings(Embeddings):
    def __init__(
            self,
            model: str,
            api_base: str,
            api_key: str = None,
    ):
        if api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.api_key = api_key
        # 
        self.model = model      # data['model']
        self.url = api_base
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        data = {
            "model": self.model,
            "input": texts
        }
        response = requests.post(
            self.url, 
            headers = self.headers,
            json = data
        )
        response.raise_for_status()
        result = response.json()
        return [item["embedding"] for item in result["data"]] 
        

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


