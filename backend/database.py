# Conexión a la Base de Datos

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Si estamos en la nube (Render), usaremos una URL de base de datos real
# Si estamos en local, creará un archivo llamado inmobiliaria.db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inmobiliaria.db")

# Ajuste necesario para SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()