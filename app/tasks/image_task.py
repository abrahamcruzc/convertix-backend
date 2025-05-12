from celery import shared_task
from app.services.image_processor import process_image
from app.db.session import get_db
from app.models.image import Image
import os

@shared_task(name="app.tasks.convert_image")
def convert_image(image_id: int, target_format: str, options: dict):
    with get_db() as db:
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            return
        
        try:
            input_path = os.path.join(settings.STORAGE_LOCAL_PATH, image.filename)
            output_filename = f"{os.path.splitext(image.filename)[0]}.{target_format}"
            output_path = os.path.join(settings.STORAGE_LOCAL_PATH, output_filename)
            
            if process_image(input_path, output_path, target_format, options):
                image.url = f"{settings.SERVER_HOST}/storage/{output_filename}"
                image.conversion_status = "completed"
            else:
                image.conversion_status = "failed"
            
            db.commit()
            
        except Exception as e:
            image.conversion_status = "failed"
            db.commit()
            raise