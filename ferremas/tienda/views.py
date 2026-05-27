from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
# Create your views here.
def tienda(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        items = orden.ordenitem_set.all()
        carritoItems = orden.get_cart_items
    else:
        items = []
        orden = {'get_carrito_total':0, 'get_cart_items':0, 'despacho':False}
        carritoItems = orden['get_cart_items']
               
    productos = Producto.objects.all()
    context = {'productos':productos, 'carritoItems':carritoItems}
    return render(request, 'tienda/tienda.html', context)

def carrito(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        items = orden.ordenitem_set.all()
        carritoItems = orden.get_cart_items
    else:
        items = []
        orden = {'get_carrito_total':0, 'get_cart_items':0, 'despacho':False}
        carritoItems = orden['get_cart_items']

    context = {'items':items, 'orden':orden, 'carritoItems':carritoItems}
    return render(request, 'tienda/carrito.html', context)

def pago(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        items = orden.ordenitem_set.all()
        carritoItems = orden.get_cart_items
    else:
        items = []
        orden = {'get_carrito_total':0, 'get_cart_items':0, 'despacho':False}
        carritoItems = orden['get_cart_items']

    context = {'items':items, 'orden':orden, 'carritoItems':carritoItems}
    return render(request, 'tienda/pago.html', context)

def catalogo(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        items = orden.ordenitem_set.all()
        carritoItems = orden.get_cart_items
    else:
        items = []
        orden = {'get_carrito_total':0, 'get_cart_items':0, 'despacho':False}
        carritoItems = orden['get_cart_items']    
    productos = Producto.objects.all()
    context = {'productos':productos,'carritoItems':carritoItems}
    return render(request, 'tienda/catalogo.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('action', action)
    print('Product', productId)
    cliente = request.user.cliente
    producto = Producto.objects.get(id=productId)
    orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
    ordenItem, created = OrdenItem.objects.get_or_create(orden=orden, producto=producto)
    
    if action == 'add':
        ordenItem.cantidad = (ordenItem.cantidad + 1)
    elif action == 'remove':
        ordenItem.cantidad = (ordenItem.cantidad - 1)

    ordenItem.save()

    if ordenItem.cantidad <= 0:
        ordenItem.delete()

    return JsonResponse('producto fue agregado', safe=False)

def processOrder(request):
    transaccion_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        total = float(data['form']['total'])
        orden.transaccion_id = transaccion_id

        if total == orden.get_carrito_total:
          orden.complete = True
          orden.save()

        if orden.despacho == True:
            DireccionDespacho.objects.create(
                cliente=cliente,
                orden=orden,
                direccion=data['despacho']['direccion'],
                ciudad=data['despacho']['ciudad'],
                comuna=data['despacho']['comuna'],
                codigo_postal=data['despacho']['codigoPostal']
            )  
    else:
        print('Usuario no esta logeado.')
    return JsonResponse('pago fue enviado...', safe=False)