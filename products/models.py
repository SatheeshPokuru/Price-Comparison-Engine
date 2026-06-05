from django.db import models

class Product(models.Model):

    title = models.CharField(max_length=300)

    product_url = models.URLField(default="")

    price = models.FloatField()

    category = models.CharField(max_length=200)

    image = models.URLField()

    rating = models.FloatField(default=0)

    description = models.TextField()

    source = models.CharField(max_length=100, default="FakeStore")

    def __str__(self):
        return self.title
    

from django.contrib.auth.models import User

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    class Meta:

        unique_together = ("user", "product")

class PriceHistory(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    price = models.FloatField()

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.product.title} - {self.price}"
    

class PriceAlert(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    old_price = models.FloatField()

    new_price = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):

        return f"{self.product.title} Alert"
    
class RecentlyViewed(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.user.username} - {self.product.title}"