if __name__ == "__main__":
    import os
    import sys
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_script_dir)
    sys.path.append(project_dir)


import re
import random
from mcp.server.fastmcp import FastMCP
from configs import tools_cfg
from retrieval.vkb.vector_factory import VectorGenerator
from retrieval.embedding import ArkEmbeddings
from configs import get_logger
logger = get_logger("__HOTEL_MCP_SERVER__")

mcp = FastMCP(
    name="HotelServer",
    description="Obtain hotel information for all attractions in China",
    version="0.1.42"
)


# Defin MCP tools
@mcp.tool()
def get_hotel_list(city: str, year: str, month: str, day: str) -> list[str]:
    """
    Retrieves detailed information about the hotel in the specified city.
    Args:
        city (str): The name of the city.
        year (int): The year for which to query ticket information, e.g., 2025.
        month (int): The month for which to query ticket information, ranging from 1 to 12.
        day (int): The day for which to query ticket information, ranging from 1 to 31.

    Returns:
        list[str]: A list of strings, where each string contains detailed information about hotel.
    """
    logger.debug("use get hotel mcp tools")
    try:
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
                                    vector_cfg['HOTEL_COLLECTION_NAME'])
        
        # search texts
        query_vector = ark_embeddings.embed_query(city)
        docs = vkb.search_by_vector(query_vector=query_vector)
        # to list[str]
        results = [doc.page_content for doc in docs]
        logger.debug(f"HOTEL_SERVER - got message of {city}, the frist message: \n{results[0]}")
        return results
    except Exception as e:
        logger.exception(e)
        return f"I'm very sorry, there was an issue with the service. Please think for yourself about the hotel in {city}."    



if __name__ == "__main__":
    logger.info("Hotel MCP Server running....")
    mcp.run(transport='stdio')

#    x = get_hotel_list(city='BeiJing',year=2025, month=4,day=25)
#    for item in x:
#        print(item)