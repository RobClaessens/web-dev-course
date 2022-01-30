from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    image = models.URLField(default='', blank=True, null=True)
    category = models.ForeignKey(Category, default='', blank=True, null=True, on_delete=models.SET_DEFAULT, related_name="listings")

    @property
    def highest_bid(self):
        return max([bid.bid for bid in self.bids.all()], default=self.starting_bid)

    @property
    def number_of_bids(self):
        return len(self.bids.all())

    def __str__(self):
        return self.title


class Bid(models.Model):
    bid = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')


class Comment(models.Model):
    comment = models.CharField(default='', max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')


class Watching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchings')
