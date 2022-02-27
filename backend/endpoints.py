import pathlib
from uuid import uuid4
from typing import List, Optional

import aiofiles
from webpreview import web_preview
from fastapi import Depends, Path, File, Body, Form, Query, UploadFile, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .models import User, Post, Message, Error
from .mock_data import default_users, default_posts


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_hash_password(password: str):
    return "fakehashed" + password


def get_user(db, username: str):
    if username in db:
        user = db[username]
        return user


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(default_users, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = default_users.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.post(
    "/users/register",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    responses={status.HTTP_409_CONFLICT: {"model": Error}},
)
async def register_user(user: User = Body(...)):
    if user.username in default_users:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=Error(message="Username already exists!", status_code=status.HTTP_409_CONFLICT).dict()
        )
    default_users[user.username] = user
    return user


@app.get("/users/me",
    status_code=status.HTTP_200_OK,
    response_model=User,
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get(
    "/posts",
    status_code=status.HTTP_200_OK,
    response_model=List[Post],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error}},
)
async def get_posts(
    offset: int = Query(default=0, example=0), 
    limit: int = Query(default=20, example=20),
) -> List[Post]:
    return list(default_posts.values())[offset:offset+limit]


@app.get(
    "/posts/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=Post,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error},
    },
)
async def get_post(
    post_id: str = Path(..., title="The ID of the item to get", example="cf23df22"),
) -> Post:
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
    media: List[UploadFile] = [], 
    text: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
) -> Post:
    post_id = uuid4().hex

    title = description = preview = None
    if link:
        title, description, preview = web_preview(url=link)

    media_paths = []
    if media:
        for m in media:
            path = pathlib.Path(f"data/files/{current_user.username}/{m.filename}")
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, 'wb') as f:
                content = await m.read()
                await f.write(content)
                media_paths.append(m.filename)

    post = Post(
        post_id=post_id,
        username=current_user.username,
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
async def delete_post(
    post_id: str = Path(..., title="The ID of the item to delete", example="cf23df22"),
    current_user: User = Depends(get_current_active_user),
) -> Post:
    if post_id in default_posts:
        post = default_posts[post_id]
        if post.username != current_user.username:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=Error(message="You are not an author!", status_code=status.HTTP_401_UNAUTHORIZED).dict(),
            )
        del default_posts[post_id]
        return post
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
async def like_post(
    post_id: str = Path(..., title="The ID of the post to like", example="cf23df22"),
    current_user: User = Depends(get_current_active_user),
) -> Message:
    if post_id in default_posts:
        post = default_posts[post_id]
        if current_user.username in post.likes:
            del post.likes[current_user.username]
            return Message(message=f"Like for post {post_id} removed!")
        else:
            post.likes[current_user.username] = 1
            return Message(message=f"Like for post {post_id} added!")
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Error(message="Post does not exist", status_code=status.HTTP_404_NOT_FOUND).dict(),
        )