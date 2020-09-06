from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing")

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.PositiveIntegerField()
    cat = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    image_url = models.CharField(max_length=512, null=True)
    current_price = models.PositiveIntegerField(default=0)
    last_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="winnings")

    def __str__(self):
        return f"{self.title} by {self.owner.username}"

class Category(models.Model):
    title = models.CharField(max_length=32, null=True)
    listings = models.ManyToManyField(Listing)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userbids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listbids")
    bid = models.PositiveIntegerField()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingcomments")
    content = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)