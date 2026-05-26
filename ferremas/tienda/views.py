from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
# Create your views here.
def tienda(request):
	productos = Producto.objects.all()
	context = {'productos':productos}
	return render(request, 'tienda/tienda.html', context)

def carrito(request):
     if request.user.is_authenticated:
      cliente = request.user.cliente
      orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
      items = orden.ordenitem_set.all()
     else:
          items = []
          orden = {'get_carrito_total':0, 'get_cart_items':0}

     context = {'items':items, 'orden':orden}
     return render(request, 'tienda/carrito.html', context)

def pago(request):
     if request.user.is_authenticated:
      cliente = request.user.cliente
      orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
      items = orden.ordenitem_set.all()
     else:
          items = []
          orden = {'get_carrito_total':0, 'get_cart_items':0}

     context = {'items':items, 'orden':orden}
     return render(request, 'tienda/pago.html', context)

def catalogo(request):
	productos = Producto.objects.all()
	context = {'productos':productos}
	return render(request, 'tienda/catalogo.html', context)

def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
     print('action', action)
     print('Product', productId)
     return JsonResponse('Item was added', safe=False)