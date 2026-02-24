from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from decimal import Decimal
import json

from .forms import ProductForm
from .models import Order, OrderItem, Product
from .serializers import ProductSerializer


def home(request):
    products = Product.objects.select_related('category').order_by('name')
    return render(request, 'home.html', {'products': products})


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            messages.error(request, 'Admin access only.')
        else:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_staff, login_url='login')(view_func))


@admin_required
def dashboard(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.select_related('category').order_by('name')

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    total_revenue = Order.objects.aggregate(total=Sum('total_amount')).get('total') or Decimal('0.00')

    context = {
        'products': products,
        'query': query,
        'product_count': Product.objects.count(),
        'low_stock_count': Product.objects.filter(stock__lt=10).count(),
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard.html', context)


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully.')
        return redirect('dashboard')
    return render(request, 'product_form.html', {'form': form, 'title': 'Add Product'})


@admin_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('dashboard')
    return render(request, 'product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('dashboard')
    return render(request, 'product_confirm_delete.html', {'product': product})


@admin_required
def product_stock_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        amount_raw = request.POST.get('amount', '1')

        try:
            amount = max(1, int(amount_raw))
        except ValueError:
            amount = 1

        if action == 'add':
            product.stock += amount
            messages.success(request, f'Stock increased by {amount}.')
        elif action == 'reduce':
            product.stock = max(0, product.stock - amount)
            messages.success(request, f'Stock reduced by {amount}.')
        product.save(update_fields=['stock'])

    return redirect('dashboard')


def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    try:
        payload = json.loads(request.body)
        items = payload.get('items', [])

        if not isinstance(items, list) or not items:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty.'}, status=400)

        normalized_items = {}
        for item in items:
            product_id = int(item.get('id', 0))
            quantity = int(item.get('quantity', 0))

            if product_id <= 0 or quantity <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid cart item.'}, status=400)

            normalized_items[product_id] = normalized_items.get(product_id, 0) + quantity

        products = Product.objects.in_bulk(list(normalized_items.keys()))
        if len(products) != len(normalized_items):
            return JsonResponse({'status': 'error', 'message': 'Some products were not found.'}, status=404)

        total_amount = Decimal('0.00')
        for product_id, qty in normalized_items.items():
            product = products[product_id]
            if product.stock < qty:
                return JsonResponse(
                    {'status': 'error', 'message': f'Not enough stock for {product.name}.'},
                    status=400,
                )
            total_amount += Decimal(str(product.price)) * qty

        if request.user.is_authenticated:
            order_user = request.user
        else:
            order_user, _ = User.objects.get_or_create(username='guest_customer', defaults={'is_active': True})

        with transaction.atomic():
            order = Order.objects.create(user=order_user, total_amount=total_amount)
            for product_id, qty in normalized_items.items():
                product = products[product_id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price_at_time_of_order=product.price,
                )
                product.stock -= qty
                product.save(update_fields=['stock'])

        return JsonResponse({'status': 'success', 'order_id': order.id})

    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request data.'}, status=400)


@admin_required
def revenue_page(request):
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')
    total_revenue = orders.aggregate(total=Sum('total_amount')).get('total') or Decimal('0.00')

    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'order_count': orders.count(),
    }
    return render(request, 'revenue.html', context)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all().order_by('id')
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all().order_by('id')

        name = self.request.query_params.get('name')
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        in_stock = self.request.query_params.get('in_stock')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock in {'1', 'true', 'True'}:
            queryset = queryset.filter(stock__gt=0)

        return queryset
