if __name__ == "__main__":
    import os
    import sys
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_script_dir)
    sys.path.append(project_dir)

    
# ticket server simulate
import re
import random
from mcp.server.fastmcp import FastMCP
from configs.config import tools_cfg
from retrieval.vkb.vector_factory import VectorGenerator
from retrieval.embedding import ArkEmbeddings
from configs import get_logger
logger = get_logger("__ATTRACTION_MCP_SERVER__")

# Create MCP server instance

mcp = FastMCP(
    name="AttractionServer",
    description="Obtain attraction information for all attractions in China and whether there are any remaining tickets",
    version="0.1.42"
)

def is_attraction_support_sml(attraction_name: str) -> bool:
    # not suport 30%,  70% suport.
    return random.random() < 0.7

def get_ticket_message_sml(city: str, attraction_name:str, year: int, month: int, day: int) -> dict:
    """
    Return:
        state message
        attraction_code: f0000(free ticket), s0000~s9999(attraction_code), x0000(not support or no ticekt)
    """
    if is_attraction_support_sml(attraction_name=attraction_name):
        # Simulate whether there are any remaining tickets
        sml = random.random() 
        if sml < 0.5:
            return {
                "state_message": "This scenic area does not require admission tickets",
                "attraction_code": "f0000"
            }
        elif sml < 0.9:
            ticket_code = f"s{random.randint(1000, 9999)}"
            return {
                "state_message": "There are remaining tickets for this scenic spot",
                "attraction_code": ticket_code    
            }
        else:
            return {
                "state_message": "There are no remaining tickets in the scenic area during the current period", 
                "attraction_code":"x0000"
            }
    else:
        return {
            "state_message": "The current scenic spot is no longer within the supported range. Please choose another one.", 
            "attraction_code":"x0000"
        }


def booking_ticket_sml(attraction_code: str) -> str:
    if check_string_format(attraction_code):
        if attraction_code[0] == "s":
            return f"Booking {attraction_code} success."
        elif attraction_code[0] == "f":
            return f"This scenic area is free."
        else:
            # start with x
            return "Booking error, no ticket."
    else:
        return "Booking error, attraction code error."


def check_string_format(attraction_code: str) -> bool:
    pattern = r'^[a-z]\d{4}$'
    return bool(re.match(pattern, attraction_code))

# Define MCP tools'

@mcp.tool()
def get_attractions_list(city: str) -> list[str]:
    """
    Retrieves detailed information about the famous scenic spots in the specified city.
    Args:
        city (str): The name of the city for which to fetch attraction information.
    Returns:
        list[str]: A list of strings, where each string contains detailed information about a scenic spot in the specified city.
    """
    logger.debug("use get attractions tool")
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
                                    vector_cfg['ATTRACTION_COLLECTION_NAME'])
        
        # search texts
        query_vector = ark_embeddings.embed_query(city)
        docs = vkb.search_by_vector(query_vector=query_vector)
        # to list[str]
        results = [doc.page_content for doc in docs]
        logger.debug(f"ATTRACTION_SERVER - got message of {city}, the frist message: \n{results[0]}")
        return results
    except Exception as e:
        logger.exception(e)
        return f"I'm very sorry, there was an issue with the service. Please think for yourself about the attractions in {city}."    



@mcp.tool()
def get_ticket_message(city: str, attraction_name:str, year:int, month:int, day:int) -> dict[str, str]:
    """
    Get ticket information for a specified attraction in a given city on a specific date.
    Parameters:
        city (str): The name of the city where the attraction is located, e.g., "Nanjing", "Shanghai".
        attraction_name (str): The name of the attraction, e.g., "Dr. Sun Yat-sen Mausoleum", "The Bund".
        year (int): The year for which to query ticket information, e.g., 2025.
        month (int): The month for which to query ticket information, ranging from 1 to 12.
        day (int): The day for which to query ticket information, ranging from 1 to 31.

    Returns:
        dict: { 'state_message': 'A string containing ticket information. ', 'attraction_code': 'scenic area code just a code for booking_ticket tools'}
        """

    x =  get_ticket_message_sml(city, attraction_name, year,month, day)
    logger.info(f"ATTRACTION_SERVER - GET_TICKET_MESSAGE: {x}")
    return x

@mcp.tool()
def booking_ticket(attraction_code: str) -> str:
    """
    Book tickets for the attraction corresponding to the specified attraction code.
    Parameters:
        attraction_code (str): The unique code of the attraction, used to identify the attraction for which tickets are to be booked. This code needs to meet specific format requirements.

    Returns:
        str: A string containing the booking result.
    """
    x = booking_ticket_sml(attraction_code=attraction_code)
    logger.info(f"ATTRACTION_SERVER - BOOKING_TICKET {x}")
    return x


@mcp.tool()
def get_ticket_price(attraction_code: str) -> int:
    """
    Get the price of the ticket
    Parameters:
        attraction_code(str): The unique code of the attraction, used to identify the attraction for which tickets are to be booked. This code needs to meet specific format requirements.

    Retruns:
        int: The Price of ticket
    """
    logger.debug("ATTRACTION_SERVER - GET TICKET PRICE")
    if check_string_format(attraction_code):
        if attraction_code[0] == "s":
            return random.randint(25, 200)
        elif attraction_code[0] == "f":
            return 0
        else:
            # start with x
            return 0
    else:
        return 0



# Start server
if __name__ == "__main__":
    logger.info("Atrraction Ticket MCP Server running...")
    mcp.run(transport='stdio') 
    # get_ticket_message(attraction_name='太空电梯', city='阿斯瓦尔', day=25, month= 4, year= 2024)
    # print(get_attractions_list(city="beijing"))
