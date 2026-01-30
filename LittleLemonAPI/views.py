from django.shortcuts import render
from rest_framework import generics, filters, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from .permissions import IsManager, IsDeliveryCrew

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    search_fields = ['title']
    filter_backends = [filters.OrderingFilter,
                       filters.SearchFilter,]
    
    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug__iexact=category)
        return queryset

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [permissions.IsAuthenticated, IsManager]
        else: 
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [permissions.IsAuthenticated, IsManager]
        else: 
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

class BaseGroupListView(APIView):
    permission_classes = [IsManager]
    group_name = None

    def get(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=self.group_name)
        group.user_set.add(user)
        return Response({'message': f'User {username} added to {self.group_name} group.'}, status=status.HTTP_201_CREATED)
    
class BaseGroupRemoveView(APIView):
    permission_classes = [IsManager]
    group_name = None

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        group = get_object_or_404(Group, name=self.group_name)
        group.user_set.remove(user)
        return Response({'message': f'User {user.username} removed from {self.group_name} group.'}, status=status.HTTP_200_OK)
    
class ManagerListView(BaseGroupListView):
    group_name = 'Manager'

class ManagerRemoveView(BaseGroupRemoveView):
    group_name = 'Manager'

class DeliveryCrewListView(BaseGroupListView):
    group_name = 'Delivery Crew'

class DeliveryCrewRemoveView(BaseGroupRemoveView):
    group_name = 'Delivery Crew'

class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_200_OK)
    
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['status', 'date']
    search_fields = ['user__username', 'delivery_crew__username']
    filter_backends = [filters.OrderingFilter,
                       filters.SearchFilter,]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            queryset = Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            queryset = Order.objects.filter(delivery_crew=user)
        else:
            queryset = Order.objects.filter(user=user)

        status_param = self.request.query_params.get('status')
        if status_param is not None:
            if status_param.lower() == 'true':
                queryset = queryset.filter(status=True)
            elif status_param.lower() == 'false':
                queryset = queryset.filter(status=False)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Cart is empty.")
        total = sum(item.price for item in cart_items)
        order = serializer.save(user=user, total=total, status=False, delivery_crew=None)
        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            ) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
    
    def patch(self, request, *args, **kwargs):
        user = request.user
        is_manager = user.groups.filter(name='Manager').exists()
        is_delivery_crew = user.groups.filter(name='Delivery Crew').exists()

        if is_manager:
            return self.partial_update(request, *args, **kwargs)
        elif is_delivery_crew:
            order = self.get_object()
            stat = request.data.get('status')
            if stat is not None:
                order.status = stat
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({'error': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)