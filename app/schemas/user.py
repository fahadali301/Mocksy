from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes= True

class UserLogin(BaseModel):
    email: str
    password: str