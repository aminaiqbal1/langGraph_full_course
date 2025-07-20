from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

Database_url="postgresql://neondb_owner:npg_Rcpv1lqGLU4g@ep-dark-silence-a4624kr8-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(Database_url, reload=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal() # for making connection with database
    try:
        yield db # for creating session
    finally:
        db.close() # for closing session