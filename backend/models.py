from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str = Field(..., example="i0XDiOlQS9YDPyGooNJ1oRpFj7d2")


class Post(BaseModel):
    post_id: str = Field(..., example="cf23df22")

    text: str = Field(..., example="Here is a nice post: https://realpython.com/python-redis/")

    media: List[str] = Field([], example=["https://cutt.ly/EPmDOV5"])

    link_title: Optional[str] = Field(None, example="How to Use Redis With Python – Real Python")
    link_description: Optional[str] = Field(None, example="In this step-by-step tutorial, you'll cover how to use both Redis and its Python client library. You'll learn a bite-sized slice of Redis itself and master the redis-py client library.")
    link_preview: Optional[str] = Field(None, example="https://files.realpython.com/media/A-Guide-to-Redis--Python_Watermarked.fadbf320f71f.jpg")
    
    likes: Dict[str, int] = Field({}, example={"i0XDiOlQS9YDPyGooNJ1oRpFj7d2": 1})

    def flatten(self) -> Dict[str, Any]:
        result =  {
            f"{self.post_id}:post_id": self.post_id,
            f"{self.post_id}:text": self.text,
            f"{self.post_id}:media": self.media,
            f"{self.post_id}:link:title": self.link_title,
            f"{self.post_id}:link:description": self.link_description,
            f"{self.post_id}:link:preview": self.link_preview,            
        }
        for user, likes in self.likes.items():
            result[f"{self.post_id}:likes:{user}"] = likes

    # @classmethod
    # def from_redis(cls, data: Dict[str, Any]) -> "Post":
    #     likes = {}
    #     for k, v in data[] 

class Message(BaseModel):
    message: str


class Error(Message):
    status_code: int