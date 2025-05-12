from PIL import Image
import os
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logger import logger

def process_image(
    input_path: str,
    output_path: str,
    target_format: str,
    options: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Procesa y convierte una imagen al formato especificado.
    
    Args:
        input_path: Ruta al archivo de imagen original
        output_path: Ruta donde se guardará la imagen convertida
        target_format: Formato objetivo de la conversión
        options: Opciones adicionales para el procesamiento
    
    Returns:
        bool: True si la conversión fue exitosa, False en caso contrario
    """
    try:
        # Asegurarse de que el formato es válido
        if target_format.lower() not in settings.ALLOWED_IMAGE_FORMATS:
            raise ValueError(f"Formato no soportado: {target_format}")
        
        # Abrir la imagen
        with Image.open(input_path) as img:
            # Aplicar opciones de procesamiento si existen
            if options:
                if 'resize' in options:
                    width = options['resize'].get('width')
                    height = options['resize'].get('height')
                    if width and height:
                        img = img.resize((width, height))
                
                if 'rotate' in options:
                    angle = options['rotate']
                    img = img.rotate(angle)
                
                if 'quality' in options:
                    quality = options['quality']
                else:
                    quality = 85  # Calidad por defecto
            
            # Asegurarse de que el directorio de salida existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar la imagen convertida
            if target_format.lower() in ['jpg', 'jpeg']:
                # Convertir a RGB si es necesario para JPEG
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
            
            img.save(
                output_path,
                format=target_format.upper(),
                quality=quality if target_format.lower() in ['jpg', 'jpeg'] else None
            )
            
            return True
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}")
        return False