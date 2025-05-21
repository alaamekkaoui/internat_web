import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import io

def handle_file_upload(file, upload_dir='uploads', filename_prefix=''):
    """
    Handle file upload with validation and error handling
    
    Args:
        file: The file object from request.files
        upload_dir: Directory to save the file (default: 'uploads')
        filename_prefix: The complete filename to use (e.g., 'lastname_firstname.jpg')
    
    Returns:
        dict: {
            'success': bool,
            'filename': str or None,
            'file_path': str or None,
            'error': str or None
        }
    """
    try:
        print("\n=== File Upload Process Started ===")
        
        # 1. Check if file is present
        if not file:
            print("❌ No file provided")
            return {'success': False, 'error': 'No file provided'}

        print(f"📁 Received file: {file.filename}")
        
        # 2. Check if file is empty
        if file.filename == '':
            print("❌ No selected file")
            return {'success': False, 'error': 'No selected file'}

        # 3. Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        file_ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
        if file_ext not in allowed_extensions:
            print(f"❌ Invalid file type: {file_ext}")
            return {'success': False, 'error': f'Invalid file type: {file_ext}'}

        # 4. Create uploads directory if it doesn't exist
        try:
            os.makedirs(upload_dir, exist_ok=True)
            print(f"📂 Uploads directory: {os.path.abspath(upload_dir)}")
        except Exception as e:
            print(f"❌ Error creating uploads directory: {str(e)}")
            return {'success': False, 'error': 'Error creating uploads directory'}

        # 5. Use the provided filename (which should already include the extension)
        filename = secure_filename(filename_prefix)
        file_path = os.path.join(upload_dir, filename)
        print(f"📝 Using filename: {filename}")
        print(f"📝 Full file path: {os.path.abspath(file_path)}")

        # 6. Process and save the image
        try:
            # Read the image
            img = Image.open(file)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Save the image in the specified format with consistent quality
            if filename.lower().endswith('.png'):
                img.save(file_path, 'PNG', optimize=True)
            else:
                img.save(file_path, 'JPEG', quality=95, optimize=True)
            
            print("✅ File saved successfully")
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
            return {'success': False, 'error': 'Error saving file'}

        # 7. Verify file was saved
        if not os.path.exists(file_path):
            print("❌ File not found after save!")
            return {'success': False, 'error': 'File was not saved properly'}

        print(f"✅ File exists at path: {file_path}")
        print(f"📊 File size: {os.path.getsize(file_path)} bytes")
        print("=== File Upload Process Completed ===\n")

        return {
            'success': True,
            'filename': filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path)
        }

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {'success': False, 'error': str(e)} 