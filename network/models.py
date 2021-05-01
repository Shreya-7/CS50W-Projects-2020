from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField(
        'self', related_name='following', symmetrical=False, blank=True)

    following_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)


class Post(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField()
    likes = models.IntegerField(default=0)
    poster = models.ForeignKey(
        User, related_name='posts', on_delete=models.CASCADE)
    likers = models.ManyToManyField(User, related_name='likes', blank=True)

    def __str__(self):
        return f'By {self.poster.username} at {self.timestamp}'
