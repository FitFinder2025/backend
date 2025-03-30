import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import uuid
from gemini import get_image_description

client = chromadb.Client()
embedding_function = OpenCLIPEmbeddingFunction()
collection = client.get_or_create_collection(
    name='multimodal_collection3',
    embedding_function=embedding_function,
    data_loader=ImageLoader()
)


def add_to_closet_db(image_path, description, cloth_type):
    image_id = str(uuid.uuid4())
    collection.add(
        uris=[image_path],
        ids=[image_id],
        metadatas=[{'type': cloth_type, 'description': description}]
    )

def get_closet_count():
    return collection.count()

   

