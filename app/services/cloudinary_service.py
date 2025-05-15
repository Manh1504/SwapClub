import cloudinary
import cloudinary.uploader
import os
from flask import current_app


def init_cloudinary():
    # Cấu hình Cloudinary từ biến môi trường
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )


def upload_image(file, folder="products"):
    """
    Upload ảnh lên Cloudinary

    Args:
        file: File ảnh từ form
        folder: Thư mục lưu trên Cloudinary

    Returns:
        dict: Thông tin về ảnh đã upload (url, public_id, v.v.)
    """
    if not file:
        return None

    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'thumbnail': cloudinary.utils.cloudinary_url(
                result['public_id'],
                width=200,
                height=200,
                crop="fill"
            )[0]
        }
    except Exception as e:
        print(f"Lỗi upload ảnh lên Cloudinary: {e}")
        return None


def delete_image(public_id):
    """
    Xóa ảnh từ Cloudinary

    Args:
        public_id: ID công khai của ảnh

    Returns:
        bool: True nếu xóa thành công, False nếu thất bại
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Lỗi khi xóa ảnh từ Cloudinary: {e}")
        return False