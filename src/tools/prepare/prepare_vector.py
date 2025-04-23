from tools.retrieval.vkb.vector_factory import VectorGenerator
from tools.config import tools_cfg
from tools.retrieval.splitter import StructuredSplitter
from tools.retrieval.embedding import ArkEmbeddings
from tools.retrieval.document import Document
from tp_logger import get_logger
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

# attractions
attraction_collection = vector_cfg['ATTRACTION_COLLECTION_NAME']
attraction_file_path = vector_cfg["ATTRACTION_FILE_PATH"]

# init vkb and add texts
vkb = vkb_generator.get_vector('elasticsearch',attraction_collection)
vkb.get_health()

if not vkb.collection_exist():
    logger.info(f"try to create index: {attraction_collection}")
    docs = sp.split_file(file_path=attraction_file_path, 
                  structured_fields={"City","Attraction_Name"})
    docs = embed_document(docs=docs)
    vkb.create(texts=docs)
    logger.info(f"vector {attraction_collection} is created.")
    # vkb.delete()
else:
    logger.info(f"vector {attraction_collection} is existed.")

