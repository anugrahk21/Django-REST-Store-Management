from rest_framework import viewsets
from .models import Product # we put '.' because we are importing from the same folder
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Product.objects.all()
        name = self.request.query_params.get('name', None)
        category = self.request.query_params.get('category', None)
        if name:
            queryset = queryset.filter(name=name)
        if category:
            queryset = queryset.filter(category=category)
        return queryset