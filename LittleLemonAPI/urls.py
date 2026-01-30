from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view(), name='menu-items'),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view(), name='single-menu-item'),
    path('groups/manager/users', views.ManagerListView.as_view(), name='manager-list'),
    path('groups/manager/users/<int:pk>', views.ManagerRemoveView.as_view(), name='manager-remove'),
    path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view(), name='delivery-crew-list'),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view(), name='delivery-crew-remove'),
    path('cart/menu-items', views.CartView.as_view(), name='cart'),
    path('orders', views.OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
]