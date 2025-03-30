import base64
import os
from google import genai
from google.genai import types
import json
import PIL.Image
from dotenv import load_dotenv
from enum import Enum
load_dotenv()

api_key = os.getenv("API_KEY")


class ClothingColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    WHITE = "white"
    GRAY = "gray"
    BROWN = "brown"
    PINK = "pink"
    PURPLE = "purple"
    ORANGE = "orange"
    KHAKI = "khaki"
    BEIGE = "beige"
    NAVY = "navy"
    OLIVE = "olive"
    MAROON = "maroon"
    TEAL = "teal"
    CYAN = "cyan"
    MAGENTA = "magenta"
    LIME = "lime"
    SILVER = "silver"
    GOLD = "gold"


def get_image_description(image_path):
    image = PIL.Image.open(image_path)
    client = genai.Client(api_key=api_key)
    model_gem = "gemini-2.0-flash"
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["description", "cloth_type"],
            properties={
                "description": genai.types.Schema(type=genai.types.Type.STRING),
                "cloth_type": genai.types.Schema(
                    type=genai.types.Type.STRING,
                    enum=["TOP_ACCESSORIES", "LOWER_WEAR", "MIDDLE_WEAR", "SHOES"]
                ),
            },
        ),
    )
    prompt = """You will be given a picture of a clothing article. Please provide a detailed description suitable for searching, and classify its type. Generate valid JSON in this schema: { "description": str, "cloth_type": str }.

For the "description", identify the specific **type of garment** (e.g., t-shirt, jeans, dress, sneakers). Include details about any prominent **patterns** (e.g., striped, floral, solid), the **material** if discernible (e.g., denim, cotton, leather), and the overall **style** or **vibe** (e.g., casual, formal, sporty, vintage). If a brand is clearly visible, mention it.

For the "cloth_type", based on your description, choose the most appropriate category from the following list: "TOP_ACCESSORIES"(caps, toques, beanies), "LOWER_WEAR"(pants, jeans, trousers), "MIDDLE_WEAR"(tshirts, jackets, full sleeves shirts, shirts), "SHOES". Choose only one category.
"""

    response = client.models.generate_content(
    model = model_gem,
    contents=[prompt, image],
    config=generate_content_config
    )
    description = None
    cloth_type = None
    try:
        json_output = json.loads(response.text)
        description = json_output.get("description")
        cloth_type = json_output.get("cloth_type")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in get_image_description: {e}")
        print(f"Raw response text: {response.text}")

    color = get_image_color(image_path)
    return description, cloth_type, color

    
def get_image_color(image_path):
    image = PIL.Image.open(image_path)
    client = genai.Client(api_key=api_key)
    model_gem = "gemini-2.0-flash"
    color_values = [color.value for color in ClothingColor]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["color"],
            properties={
                "color": genai.types.Schema(
                    type=genai.types.Type.STRING,
                    enum=color_values
                )
            },
        ),
    )
    prompt = f"""You will be given a picture of a clothing article. Identify the single most dominant color of the clothing item and provide it as one word. Choose the color from the following list: {', '.join(color_values)}. Respond with only the lowercase color name. Generate valid JSON in this schema: {{ "color": str }}."""

    response = client.models.generate_content(
    model = model_gem,
    contents=[prompt, image],
    config=generate_content_config
    )
    try:
        json_output = json.loads(response.text)
        color_str = json_output.get("color")
        if color_str in color_values:
            return color_str
        else:
            print(f"Warning: Gemini returned color '{color_str}' which is not in the predefined list.")
            return None # Or you could return a default color like "unknown"
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in get_image_color: {e}")
        print(f"Raw response text: {response.text}")
        return None