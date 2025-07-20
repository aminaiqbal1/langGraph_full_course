from fastapi import FastAPI, Depends, HTTPException, File, UploadFile # for creating API
from sqlalchemy.orm import Session # ak mrtaba session create hojyga hum bar bar us ka sath kaam krenge
from database import engine, get_db# for making connection with database
from models import Singup, Food, Order# for creating table
from typing import List # for creating list
from utils import SinupCreate, SinupResponse # for validation and serialization
from fastapi.middleware.cors import CORSMiddleware # for allowing cross origin requests
Singup.metadata.create_all(bind=engine) # ya alumbic ki trhn he kaam krta hai mgr s mn verson create n hoty hain
# for creating table in database
app = FastAPI() # for creating API


@app.put("/{name}")
def  intro(name):
    return name

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# this command is use for createing and changeing for every table, column, 

# alembic revision --autogenerate -m "create pdf_data table"
# alembic upgrade head