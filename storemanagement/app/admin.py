from django.contrib import admin
from .models import Category, Order, OrderItem, Product


admin.site.register(Category)
admin.site.register(Product)


# Show OrderItems inside the Order detail page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'created_at')
    inlines = [OrderItemInline]


# Combined flat view: shows id, user, product, quantity, per price, total price
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'get_user', 'product', 'quantity', 'price_at_time_of_order', 'line_total')

    def order_id(self, obj):
        return obj.order.id
    order_id.short_description = 'Order ID'

    def get_user(self, obj):
        return obj.order.user.username
    get_user.short_description = 'User'

    def line_total(self, obj):
        return obj.quantity * obj.price_at_time_of_order
    line_total.short_description = 'Total Price'
