from database import collection
import numpy as np
from PIL import Image

import os
from config import ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_numpy_array(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        img_array = np.array(img)
        return img_array
    except Exception as e:
        print(f"Error converting image to NumPy array: {e}")
        return None