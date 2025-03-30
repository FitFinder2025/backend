import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MONGODB_URI = "mongodb+srv://hoohacks:hoohacks123@closet.f961q.mongodb.net/closet_app_db?retryWrites=true&w=majority&appName=closet&ssl=true&ssl_cert_reqs=CERT_NONE"