from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass

    @property
    def watchlist_listings(self):
        return [watching.listing for watching in self.watchlist.all()]


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    @property
    def highest_bid_object(self):

        # Return highest bid object, returns None if no bids available yet
        return max(self.bids.all(), key=lambda bid: bid.bid, default=None)

    @property
    def highest_bid_value(self):

        # Return highest bid value, return starting bid if no bids available yet
        return self.highest_bid_object.bid if self.highest_bid_object else self.starting_bid

    @property
    def number_of_bids(self):
        return len(self.bids.all())

    @property
    def sorted_bids(self):
        return sorted(self.bids.all(), key=lambda bid: bid.bid, reverse=True)
    
    @property
    def number_of_comments(self):
        return len(self.comments.all())

    @property
    def sorted_comments(self):
        return sorted(self.comments.all(), key=lambda comment: comment.created_at, reverse=True)

    @property
    def number_of_watchings(self):
        return len(self.watchings.all())

    def __str__(self):
        return self.title


class Bid(models.Model):
    bid = models.DecimalField(default=0, max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid on '{self.listing.title}' of €{self.bid} from '{self.user}'"


class Comment(models.Model):
    comment = models.CharField(default='', max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on '{self.listing.title}' from '{self.user}'"


class Watching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchings')
    created_at = models.DateTimeField(auto_now_add=True)
