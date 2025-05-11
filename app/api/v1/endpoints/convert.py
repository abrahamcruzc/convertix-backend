from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.image import Image, ImageCreate, ImageOut, ConversionRequest
from app.core.config import settings
from app.services.image_processor import process_image
from app.core.celery_app import celery_app

router = APIRouter()

@router.post("/upload", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube una imagen al sistema.
    """
    # Validar el tamaño del archivo
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo es demasiado grande. Máximo permitido: {settings.MAX_IMAGE_SIZE} bytes"
        )
    
    # Validar el formato
    format = file.filename.split('.')[-1].lower()
    if format not in settings.ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Formatos permitidos: {settings.ALLOWED_IMAGE_FORMATS}"
        )
    
    # Crear registro de imagen
    image_data = {
        "filename": file.filename,
        "format": format,
        "size": len(content),
        "url": f"/storage/{file.filename}",  # URL temporal
        "original_format": format
    }
    
    db_image = Image(**image_data)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    # Guardar el archivo
    # Aquí implementaremos el almacenamiento más adelante
    
    return db_image

@router.post("/convert/{image_id}", response_model=ImageOut)
async def convert_image(
    image_id: int,
    conversion: ConversionRequest,
    db: Session = Depends(get_db)
):
    """
    Inicia una tarea de conversión de imagen.
    """
    # Verificar que la imagen existe
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Validar el formato objetivo
    if conversion.target_format not in settings.ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato objetivo no soportado. Formatos permitidos: {settings.ALLOWED_IMAGE_FORMATS}"
        )
    
    # Actualizar el estado de la imagen
    image.conversion_status = "processing"
    image.converted_format = conversion.target_format
    db.commit()
    
    # Iniciar tarea de conversión asíncrona
    celery_app.send_task(
        "app.tasks.convert_image",
        args=[image_id, conversion.target_format, conversion.options]
    )
    
    return image

@router.get("/status/{image_id}", response_model=ImageOut)
async def get_conversion_status(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado actual de una conversión.
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    return image

@router.get("/formats", response_model=List[str])
async def get_supported_formats():
    """
    Retorna la lista de formatos soportados.
    """
    return settings.ALLOWED_IMAGE_FORMATS
