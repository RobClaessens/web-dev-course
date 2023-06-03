from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name='follows', symmetrical=False)
    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def number_of_followers(self):
        return self.followers.all().count()

    @property
    def number_of_follows(self):
        return self.follows.all().count()

    @property
    def number_of_posts(self):
        return self.posts.all().count()

    @property
    def number_of_likes(self):
        return self.likes.all().count()

    @property
    def number_of_dislikes(self):
        return self.dislikes.all().count()

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "number_of_followers": self.number_of_followers,
            "number_of_follows": self.number_of_follows,
            "number_of_posts": self.number_of_posts,
            "number_of_likes": self.number_of_likes,
            "number_of_dislikes": self.number_of_dislikes,
            "time_created": self.created.strftime("%H:%M"),
            "date_created": self.created.strftime("%m/%d/%Y"),
        }


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    @property
    def number_of_likes(self):
        return self.likes.all().count()

    @property
    def number_of_dislikes(self):
        return self.dislikes.all().count()

    def __str__(self):
        return f"Post of '{self.user.username}' at {self.created.strftime('%m/%d/%Y %H:%M')}"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "username": self.user.username,
            "text": self.text,
            "number_of_likes": self.number_of_likes,
            "number_of_dislikes": self.number_of_dislikes,
            "time_created": self.created.strftime("%H:%M"),
            "date_created": self.created.strftime("%m/%d/%Y"),
        }


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f"Like of '{self.user.username}'"


class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dislikes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')

    def __str__(self):
        return f"Dislike of '{self.user.username}'"
