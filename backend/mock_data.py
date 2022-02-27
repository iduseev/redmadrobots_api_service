from .models import User, Post


default_posts = {
    "cf23df22": Post(post_id="cf23df22", username="johndoe", text="demo")
}

default_users = {
    "johndoe": User(
        username="johndoe",
        full_name="John Doe",
        email="johndoe@example.com",
        hashed_password="fakehashedsecret",
        disabled=False,
    )
}

