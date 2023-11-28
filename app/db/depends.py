from sqlalchemy.orm import Session
from app.db.connection import Session




def get_db_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()