from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., example="johndoe")
    full_name: str = Field(..., example="John Doe")
    email: str = Field(..., example="johndoe@example.com")
    hashed_password: str = Field(..., example="fakehashedsecret")
    disabled: bool = Field(False, example=False)


class Post(BaseModel):
    post_id: str = Field(..., example="cf23df22")

    username: str = Field(..., example="johndoe")

    text: str = Field(..., example="Here is a nice post: https://realpython.com/python-redis/")

    media: List[str] = Field([], example=["https://cutt.ly/EPmDOV5"])

    link_title: Optional[str] = Field(None, example="How to Use Redis With Python – Real Python")
    link_description: Optional[str] = Field(None, example="In this step-by-step tutorial, you'll cover how to use both Redis and its Python client library. You'll learn a bite-sized slice of Redis itself and master the redis-py client library.")
    link_preview: Optional[str] = Field(None, example="https://files.realpython.com/media/A-Guide-to-Redis--Python_Watermarked.fadbf320f71f.jpg")
    
    likes: Dict[str, int] = Field({}, example={"johndoe": 1})


class Message(BaseModel):
    message: str


class Error(Message):
    status_code: int
