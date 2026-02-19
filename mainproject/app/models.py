from django.db import models

# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('home', 'Home'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField()
    stock = models.IntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)