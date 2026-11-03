import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL


# Configuration de la connexion
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "iot_user"),
    password=os.getenv("DB_PASSWORD", "mot_de_passe"),
    host=os.getenv("DB_HOST", "mariadb"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "TempHumiX"),
    query={"charset": "utf8mb4"}
)

# Moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

# Création des sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Classe de base des tables
class Base(DeclarativeBase):
    pass


# Dépendance pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()