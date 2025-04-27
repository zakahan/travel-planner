from retrieval.vkb.vector_factory import VectorGenerator
from configs.config import tools_cfg
from retrieval.splitter import StructuredSplitter
from retrieval.embedding import ArkEmbeddings
from retrieval.document import Document
from configs import get_logger
logger = get_logger(__name__)

# load ark embedding
embed_cfg = tools_cfg['ark']['embedding']
ark_embeddings = ArkEmbeddings(
    model = embed_cfg['model'],
    api_base=embed_cfg['api_base'],
    api_key=embed_cfg['api_key']
)

def embed_document(docs: list[Document]) -> list[Document]:
    doc_vector_text = []
    for doc in docs:
        if doc.metadata['vector_text'] is not None:
            doc_vector_text.append(doc.metadata['vector_text'])
        else:
            doc_vector_text.append(doc.page_content)
    # embedding
    embed_list = ark_embeddings.embed_documents(doc_vector_text)
    for doc, embed in zip(docs, embed_list):
        doc.vector = embed
        pass
    return docs


# load splitter
sp = StructuredSplitter()

# load vkb
vkb_generator = VectorGenerator()
vector_cfg = tools_cfg['vectorbase']

def create_vkb(collection, file_path, fields):
    # init vkb and add texts
    vkb = vkb_generator.get_vector('elasticsearch',collection)
    vkb.get_health()

    if not vkb.collection_exist():
        logger.info(f"try to create index: {collection}")
        docs = sp.split_file(file_path=file_path, 
                    structured_fields=fields)
        docs = embed_document(docs=docs)
        vkb.create(texts=docs)
        logger.info(f"vector {collection} is created.")
        # vkb.delete()
    else:
        logger.info(f"vector {collection} is existed.")

# attractions
attraction_collection = vector_cfg['ATTRACTION_COLLECTION_NAME']
attraction_file_path = vector_cfg["ATTRACTION_FILE_PATH"]
attraction_fields = {"City","Attraction_Name"}
create_vkb(attraction_collection,
           attraction_file_path,
           attraction_fields)

# hotel
hotel_collection = vector_cfg['HOTEL_COLLECTION_NAME']
hotel_file_path = vector_cfg["HOTEL_FILE_PATH"]
hotel_fields = {'City','Hotel_Name'}
create_vkb(
    hotel_collection,
    hotel_file_path,
    hotel_fields
)
