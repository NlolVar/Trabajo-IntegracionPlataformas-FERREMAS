from django.urls import path
from . import views

urlpatterns = [
        #Leave as empty string for base url
	path('', views.tienda, name="tienda"),
	path('carrito/', views.carrito, name="carrito"),
	path('pago/', views.pago, name="pago"),
    path('catalogo/', views.catalogo, name="catalogo"),
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order")
]