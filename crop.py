import base64
import os
from google import genai
from google.genai import types
import json
from PIL import Image  # Import the Pillow library

def analyze_clothing_from_image(image_path: str) -> dict:

    client = genai.Client(
        api_key="AIzaSyBgOc2YPNlaS2HkhX42m4fBOwOWeJ3GPLA",
    )

    try:
        image = Image.open(image_path)  

      
        model = "gemini-2.0-flash"
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["crop"],
                properties = {
                    "crop": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        items = genai.types.Schema(
                            type = genai.types.Type.OBJECT,
                            required = ["category", "start_y", "end_y"],
                            properties = {
                                "category": genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                    description = "The name of the clothing category.",
                                    enum = ["TOP_ACCESSORIES", "MIDDLE_WEAR", "LOWER_WEAR", "SHOES"],
                                ),
                                "start_y": genai.types.Schema(
                                    type = genai.types.Type.INTEGER,
                                    description = "The starting vertical position of the category as a percentage from the top of the image (0-100).",
                                ),
                                "end_y": genai.types.Schema(
                                    type = genai.types.Type.INTEGER,
                                    description = "The ending vertical position of the category as a percentage from the top of the image (0-100).",
                                ),
                            },
                        ),
                    ),
                },
            ),
            system_instruction=[
                types.Part.from_text(text="""Analyze the image to identify and segment the clothing items worn by the person or displayed on the mannequin. Categorize these items into the following four groups:

        TOP_ACCESSORIES: caps, toques, beanies(no glasses)
        MIDDLE_WEAR: tshirts, shirts, jackets, vests
        LOWER_WEAR: shorts, underwears, trousers, pants, jeans
        SHOES (excluding socks)

    For each identified category, determine its vertical position within the image, measured from the top. Represent the vertical space occupied by each category as a starting and ending point on a scale from 0 to 100, where 0 is the very top of the image and 100 is the very bottom.

    Return the results in a JSON format with a single key named \"crop\". The value associated with \"crop\" should be a list of dictionaries. Each dictionary in the list should represent one of the identified categories and have the following keys:

        category: The name of the category (e.g., \"TOP_ACCESSORIES\").
        start_y: The vertical position (as a percentage from the top, 0-100) where the category begins.
        end_y: The vertical position (as a percentage from the top, 0-100) where the category ends.

    If a particular category is not present in the image, simply omit it from the \"crop\" list."""),
            ],
        )

        response = client.models.generate_content(
            model=model,
            contents=[image],
            config=generate_content_config,
        )

        if response.text:
            return json.loads(response.text)

    except FileNotFoundError:
        return {"error": f"Image file not found: {image_path}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def generate():
    # Example usage of the new function
    image_file = "Screenshot From 2025-03-24 14-08-33.png"
    if not os.path.exists(image_file):
        print(f"Error: The file '{image_file}' does not exist in the current directory.")
        return

    json_output = analyze_clothing_from_image(image_file)
    print(json.dumps(json_output, indent=2))

if __name__ == "__main__":
    generate()