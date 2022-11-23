from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    BOOKS = 'BOO'
    ELECTRONICS = 'ELE'
    FASHION = 'FAS'
    HOME = 'HOM'
    TOYS = 'TOY'
    MISC = 'MIS'
    CATEGORIES = [
        (BOOKS, 'Books'),
        (ELECTRONICS, 'Electronics'),
        (FASHION, 'Fashion'),
        (HOME, 'Home'),
        (TOYS, 'Toys'),
        (MISC, 'Miscellaneous'),
    ]

    category = models.CharField(
        max_length=3,
        choices=CATEGORIES,
        blank=False,
        default=BOOKS,
    )
    title = models.CharField(max_length=64)
    description = models.TextField()
    list_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return f"{self.user}: {self.listing} - ${self.value} ({self.timestamp})"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=200, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.listing}"
