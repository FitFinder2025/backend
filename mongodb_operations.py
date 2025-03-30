import pymongo
from config import MONGODB_URI
from gemini import get_image_color
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
embedding_function = OpenCLIPEmbeddingFunction()

client = pymongo.MongoClient(MONGODB_URI)
db = client.get_default_database()  
closet_collection = db['closet_items']

def add_item_to_closet(image_path, description, cloth_type, embedding, color):
    closet_collection.insert_one({
    "file_path": image_path,
    "description": description,
    "cloth_type": cloth_type,
    "dominant_color" : color,
    "embedding": embedding.tolist()  
})

def get_closet_item_count():
    return closet_collection.count_documents({})


def search(query_image_path, color, cloth_type=None, num_results=5):

    embed = embedding_function([query_image_path])
    embedding_vector = embed[0]
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": embedding_vector.tolist(),
                "numCandidates": 100,
                "limit": num_results,
                "score": {"type": "float"}
            }
        }
    ]

    pipeline.append({"$match": {"cloth_type": cloth_type}})
    pipeline.append({"$match": {"dominant_color": color}})


    pipeline.append({"$project": {"_id": 0, "file_path": 1, "description": 1, "cloth_type": 1, "color": 1, "score": {"$meta": "vectorSearchScore"}}})

    results = list(closet_collection.aggregate(pipeline))
    return results