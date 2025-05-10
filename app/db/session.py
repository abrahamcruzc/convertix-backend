from app.db.base import SessionLocal

def get_db():
    try:
        yield get_db
    finally:
        db.close()