module default {
  type User {
    required property user_name -> str;
    required property email -> str;
    required property full_name -> str;
    required property disabled -> bool;

  }

  type Post {
    required property text -> str;
    property title -> str;
    property description -> str;
    property preview -> str;
    property timestamp -> datetime;
    link user -> User;
  }

  type Like {
    required property count -> int32;
    link user -> User;
    link post -> Post;
  }

  type Media {
      required property uri -> str;
      link post -> Post;

  }
};