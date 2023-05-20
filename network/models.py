from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name='follows')
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


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    @property
    def number_of_likes(self):
        return self.likes.all().count()

    @property
    def number_of_dislikes(self):
        return self.dislikes.all().count()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')


class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dislikes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
