from flask import Flask, request, render_template, make_response, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from utils import allowed_file
import os
from gemini import get_image_description, get_image_color
from crop import analyze_clothing_from_image
from flask_cors import CORS
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from mongodb_operations import add_item_to_closet, get_closet_item_count, search 
from perplexity import perplexity  
from mongodb_operations import closet_collection


embedding_function = OpenCLIPEmbeddingFunction()


app = Flask(__name__)
CORS(app)  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_closet():
    if 'query_image' not in request.files:
        return jsonify({"error": "No query_image file part"})
    query_image = request.files['query_image']
    if query_image.filename == '':
        return jsonify({"error": "No selected query_image file"})
    filename = secure_filename(query_image.filename)

    print(f"Filename received in /search: {filename}")   

    query_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cloth_type = request.form.get('cloth_type')

    if query_image:
        query_image.save(query_image_path) # Save the image first
        color = get_image_color(query_image_path)
        print(color)
        results = search(query_image_path, color,  cloth_type=cloth_type)
        os.remove(query_image_path)
        json_data = jsonify(results)
        return jsonify(results)
    return jsonify({"error": "Invalid query image file type"})

@app.route('/closet', methods=['POST'])
def upload_closet():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        description, cloth_type, color = get_image_description(file_path)
        print(f"identified cloth_type as: {cloth_type}")
        embeddings = embedding_function([file_path]) 

        add_item_to_closet(file_path, description, cloth_type, embeddings[0], color)

        print(f"Number of items in closet: {get_closet_item_count()}")
        return f"Image '{filename}' added to your closet!"
    return "Invalid file type"


@app.route('/crop', methods=['POST'])
def analyze_clothing():
    if 'image' not in request.files:
        return jsonify({"error": "No image file part"})
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected image file"})
    if image_file:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        try:
            clothing_analysis_result = analyze_clothing_from_image(image_path)
            return jsonify(clothing_analysis_result)
        finally:
            os.remove(image_path) # Clean up the temporary image
    return jsonify({"error": "Invalid image file type"})

@app.route("/plex", methods=["POST"])
def plexit():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            description, cloth_type, color = get_image_description(file_path)
            print(f"Generated description for Perplexity: {description}")

            perplexity_response = perplexity(description)
            return jsonify(perplexity_response)

        except Exception as e:
            return jsonify({"error": f"An error occurred: {e}"}), 500
        finally:
            os.remove(file_path)  # Clean up the temporary file
    return jsonify({"error": "Invalid file type"}), 400
    

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_closet', methods=['GET'])
def get_closet():
    items = closet_collection.find({}, {"_id": 0, "file_path": 1})
    file_paths = [item['file_path'] for item in items]
    return jsonify(file_paths)


if __name__ == '__main__':
    app.run(debug=True)