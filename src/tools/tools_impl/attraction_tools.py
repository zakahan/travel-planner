# This part of the tool is used to interact with the vector database.
from tools.config import tools_cfg
from tools.retrieval.vkb.vector_factory import VectorGenerator
from tools.retrieval.embedding import ArkEmbeddings
from tools.retrieval.document import Document
from tp_logger import get_logger
logger = get_logger(__name__)


def get_attractions(city: str, ) -> list[str]:
    """
    Retrieves detailed information about the famous scenic spots in the specified city.
    Args:
        city (str): The name of the city for which to fetch attraction information.
    Returns:
        list[str]: A list of strings, where each string contains detailed information about a scenic spot in the specified city.
    """
    logger.debug("use get attractions tool")
    # load ark embedding
    embed_cfg = tools_cfg['ark']['embedding']
    ark_embeddings = ArkEmbeddings(
        model = embed_cfg['model'],
        api_base=embed_cfg['api_base'],
        api_key=embed_cfg['api_key']
    )
    
    # init vkb 
    vector_cfg = tools_cfg['vectorbase']

    vkb_generator = VectorGenerator()
    vkb = vkb_generator.get_vector(vector_cfg['VECTOR_TYPE'], 
                                   vector_cfg['ATTRACTION_COLLECTION_NAME'])
    
    # search texts
    query_vector = ark_embeddings.embed_query(city)
    docs = vkb.search_by_vector(query_vector=query_vector)
    # to list[str]
    results = [doc.page_content for doc in docs]
    logger.debug(f"got message of {city}, the frist message: \n{results[0]}")
    return results


if __name__ == "__main__":
    results = get_attractions(city='beijing')
    print(results)