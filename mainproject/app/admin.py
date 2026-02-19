from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'description', 'stock', 'image')  # columns shown in the table
    list_filter = ('category',)  # filter sidebar on the right
    search_fields = ('name', 'description')  # search bar at the top
