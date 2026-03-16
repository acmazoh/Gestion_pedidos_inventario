from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoVentaListView.as_view(), name='venta_list'),
]