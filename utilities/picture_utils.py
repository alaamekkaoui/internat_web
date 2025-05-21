# utilities/picture_utils.py
import os
from werkzeug.utils import secure_filename
import uuid
from flask import send_file

def save_picture(upload_folder, image_file):
    if not image_file:
        return None
    filename = secure_filename(f"{uuid.uuid4().hex}.png")
    image_path = os.path.join(upload_folder, filename)
    image_file.save(image_path)
    return filename

def get_picture(upload_folder, filename):
    image_path = os.path.join(upload_folder, filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    return None
