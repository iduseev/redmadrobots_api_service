import random
from typing import List, Optional

import aiofiles
from webpreview import web_preview
from fastapi import FastAPI, Path, status, File, Form, UploadFile
from fastapi.responses import JSONResponse

from .models import User, Post, Message, Error
from .mock_data import default_user, default_posts 


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/posts",
    status_code=status.HTTP_200_OK,
    response_model=List[Post],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error}},
)
async def get_posts() -> List[Post]:
    return list(default_posts.values())


@app.get(
    "/posts/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=Post,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error},
    },
)
async def get_post(post_id: str = Path(..., title="The ID of the item to get", example="cf23df22")) -> Post:
    if post_id in default_posts:
        return default_posts[post_id]
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Error(message="Post does not exist", status_code=status.HTTP_404_NOT_FOUND).dict(),
        )


@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=Post,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error}},
)
async def create_post(
    media: Optional[UploadFile] = None, 
    text: Optional[str] = Form(None), 
    link: Optional[str] = Form(None),
) -> Post:
    post_id = f"{random.getrandbits(32)}"

    title = description = preview = None
    if link:
        title, description, preview = web_preview(url=link)

    media_paths = []
    if media:
        async with aiofiles.open(media.filename, 'wb') as f:
            content = await media.read()
            await f.write(content)
            media_paths.append(media.filename)

    post = Post(
        post_id=post_id, 
        text=text, 
        link_title=title, 
        link_description=description, 
        link_preview=preview,
        media=media_paths,
    )

    default_posts[post_id] = post
    return post


@app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=Post,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error},
    },
)
async def delete_post(post_id: str = Path(..., title="The ID of the item to delete", example="cf23df22")) -> Post:
    if post_id in default_posts:
        result = default_posts[post_id]
        del default_posts[post_id]
        return result
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Error(message="Post does not exist", status_code=status.HTTP_404_NOT_FOUND).dict(),
        )


@app.post(
    "/likes/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error},
    },
)
async def like_post(post_id: str = Path(..., title="The ID of the post to like", example="cf23df22")) -> Message:
    if post_id in default_posts:
        post = default_posts[post_id]
        user_id = "i0XDiOlQS9YDPyGooNJ1oRpFj7d2"
        if user_id in post.likes:
            del post.likes[user_id]
            return Message(message=f"Like for post {post_id} removed!")
        else:
            post.likes[user_id] = 1
            return Message(message=f"Like for post {post_id} added!")
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Error(message="Post does not exist", status_code=status.HTTP_404_NOT_FOUND).dict(),
        )