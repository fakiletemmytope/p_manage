from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import pymysql
#X2vBHlwmNl**9VsT
SQLALCHEMY_DATABASE_URL = "sqlite:///./database/sql_app.db"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:temmytope88@db/test-db?charset=utf8mb4"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    #connect_args={"check_same_thread": False}
)

#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Session = sessionmaker(bind=engine)