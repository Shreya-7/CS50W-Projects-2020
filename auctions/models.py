from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.category_name}"
    
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    starting_bid = models.IntegerField()
    img_url = models.CharField(blank=True, max_length=200)
    category = models.ForeignKey(Category, related_name="listings", on_delete=models.SET_NULL, to_field='category_name', null=True)
    is_active = models.BooleanField()
    winner = models.ForeignKey(User, blank=True, related_name="winnings", on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, related_name="my_items", on_delete=models.SET_NULL, null=True)
    watched_by = models.ManyToManyField(User, blank=True, related_name="watching")
    current_bid = models.IntegerField(blank=True)

    def __str__(self):
        return f"{self.title} by {self.owner.username}"

class Bid(models.Model):
    bid = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_bid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")

    def __str__(self):
        return f"{self.bid} on {self.listing.title}"

class Comments(models.Model):
    comment = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_comment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} on {self.listing.title}"


