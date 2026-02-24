from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from decimal import Decimal
import json

from .forms import ProductForm
from .models import Order, OrderItem, Product
from .serializers import ProductSerializer


def home(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'home.html', {'products': products})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all().order_by('name')

    if query:
        products = products.filter(name__icontains=query)

    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    context = {
        'products': products,
        'query': query,
        'product_count': Product.objects.count(),
        'low_stock_count': Product.objects.filter(stock__lt=10).count(),
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard.html', context)


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully.')
        return redirect('dashboard')
    return render(request, 'product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('dashboard')
    return render(request, 'product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('dashboard')
    return render(request, 'product_confirm_delete.html', {'product': product})


@login_required
def product_stock_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        amount = int(request.POST.get('amount', 1))

        if action == 'add':
            product.stock += amount
            messages.success(request, f'Stock increased by {amount}.')
        elif action == 'reduce':
            product.stock = max(0, product.stock - amount)
            messages.success(request, f'Stock reduced by {amount}.')
        product.save()

    return redirect('dashboard')


def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    try:
        data = json.loads(request.body)
        items = data.get('items', [])

        if not items:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty.'}, status=400)

        # Get or create a guest user for unauthenticated customers
        if request.user.is_authenticated:
            order_user = request.user
        else:
            order_user, _ = User.objects.get_or_create(username='guest_customer')

        total_amount = Decimal('0.00')

        # Validate stock before creating the order
        for item in items:
            product = get_object_or_404(Product, id=item['id'])
            if product.stock < item['quantity']:
                return JsonResponse(
                    {'status': 'error', 'message': f'Not enough stock for {product.name}.'},
                    status=400,
                )
            total_amount += product.price * item['quantity']

        # Create the order and deduct stock
        with transaction.atomic():
            order = Order.objects.create(user=order_user, total_amount=total_amount)
            for item in items:
                product = Product.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_time_of_order=product.price,
                )
                product.stock -= item['quantity']
                product.save()

        return JsonResponse({'status': 'success', 'order_id': order.id})

    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data.'}, status=400)


@login_required
def revenue_page(request):
    orders = Order.objects.all().order_by('-created_at')
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'order_count': orders.count(),
    }
    return render(request, 'revenue.html', context)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all().order_by('id')

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
