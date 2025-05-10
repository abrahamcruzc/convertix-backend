import logging 
from sqlalchemy.orm import Session

from app.db.base import Base, engine
from app.models.user import User
from app.models.image import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:

    # Inicializa la base de datos creando las tablas.

    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")

if __name__ == "__main__":
    logger.info("Creando tablas en la base de datos...")
    init_db()
    logger.info("Tablas creadas")