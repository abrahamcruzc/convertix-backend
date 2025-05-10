from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime

from app.db.base_class import Base

class Image(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    format = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    original_format = Column(String, nullable=True)
    converted_format = Column(String, nullable=True)
    conversion_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelos Pydantic

class ImageBase(BaseModel):
    filename: str
    url: HttpUrl
    format: str
    size: int
    owner_id: Optional[int] = None
    is_active: Optional[bool] = True
    original_format: Optional[str] = None
    converted_format: Optional[str] = None
    conversion_status: Optional[str] = "pending"

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    filename: Optional[str] = None
    format: Optional[str] = None
    size: Optional[int] = None
    is_active: Optional[bool] = None
    converted_format: Optional[str] = None
    conversion_status: Optional[str] = None

class ImageOut(ImageBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Modelo para solicitar una conversión
class ConversionRequest(BaseModel):
    image_id: int
    target_format: str
    options: Optional[dict] = None

