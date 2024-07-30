from pydantic import BaseModel
from typing import Optional
class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: Optional[int]

class CreateCategory(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class CreateReview(BaseModel):
    comment: str

class CreateRating(BaseModel):
    grade: int
