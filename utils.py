from pydantic import BaseModel # for validation



def diseases(name ):
    return name 


# pydantic model for validation and serialization
class SinupCreate(BaseModel): # for creating table
    user_name : str
    password : str
    email : str
    user_id : int
    
   


class SinupResponse(SinupCreate):
    id: int

    class Config:
        orm_mode = True
