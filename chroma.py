import chromadb
from chromadb.utils import embedding_functions
from PIL import Image
import io

# Initialize ChromaDB client (in-memory for this example)
client = chromadb.Client()

# Get the OpenCLIP embedding function from ChromaDB
openclip_ef = embedding_functions.OpenCLIPEmbeddingFunction()

# Define the name of your ChromaDB collection
collection_name = "clothing_collection"

def upload_image(image_path, description):
    """
    Uploads an image to ChromaDB, generating an embedding and storing the description as metadata.

    Args:
        image_path (str): The path to the image file.
        description (str): A text description of the image.
    """
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image = Image.open(io.BytesIO(image_bytes))
        embedding = openclip_ef([image])[0]

        # Get or create the ChromaDB collection
        collection = client.get_or_create_collection(name=collection_name, embedding_function=openclip_ef)

        # Add the embedding and metadata to the collection
        collection.add(
            embeddings=[embedding],
            metadatas=[{"description": description}],
            ids=[image_path]  # Using image path as a unique ID
        )
        print(f"Image '{image_path}' uploaded successfully with description: '{description}'")

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred during upload: {e}")

def search_image(query_image_path, n_results=5):
   
    try:
        with open(query_image_path, "rb") as f:
            image_bytes = f.read()
        query_image = Image.open(io.BytesIO(image_bytes))
        query_embedding = openclip_ef([query_image])[0]

        # Get the ChromaDB collection
        collection = client.get_collection(name=collection_name, embedding_function=openclip_ef)

        # Perform the query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas"]
        )

        similar_items = []
        if results and results['ids'] and results['metadatas']:
            for i in range(len(results['ids'][0])):
                similar_items.append({
                    "id": results['ids'][0][i],
                    "description": results['metadatas'][0][i]['description']
                })
            print(f"Search results for '{query_image_path}':")
            for item in similar_items:
                print(f"- ID: {item['id']}, Description: {item['description']}")
        else:
            print("No similar images found.")

        return similar_items

    except FileNotFoundError:
        print(f"Error: Query image file not found at '{query_image_path}'")
        return []
    except Exception as e:
        print(f"An error occurred during search: {e}")
        return []

if __name__ == "__main__":
    image1_path = "clothes_dataset/shirtRed.png"
    image1_description = "A red t-shirt."

    pantBlack_path = "clothes_dataset/pantBlack.png"
    pantBlack_description = "Black pants."

    pantKhaki_path = "clothes_dataset/pantKhaki.png"
    pantKhaki_description = "Khaki pants."

    pantWhite_path = "clothes_dataset/pantWhite.png"
    pantWhite_description = "White pants."

    shoesWhite_path = "clothes_dataset/shoesWhite.png"
    shoesWhite_description = "White shoes."

    image3_path = "clothes_dataset/shirtgrey.png"
    image3_description = "A grey t-shirt."

    # Upload images to ChromaDB
    upload_image(image1_path, image1_description)
    upload_image(pantBlack_path, pantBlack_description)
    upload_image(pantKhaki_path, pantKhaki_description)
    upload_image(pantWhite_path, pantWhite_description)
    upload_image(shoesWhite_path, shoesWhite_description)
    upload_image(image3_path, image3_description)

    # Search for an image similar to another image
    query_image_path = "Untitled.png"  # Replace with the path to your query image
    search_image(query_image_path)