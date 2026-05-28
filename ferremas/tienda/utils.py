import json
from .models import *

def cookieCarrito(request):
    try:
        carroGuest = json.loads(request.COOKIES['carrito'])
    except:
        carroGuest = {}
    print('carrito:', carroGuest)

    items = []
    orden = {'get_carrito_total':0, 'get_cart_items':0, 'despacho':False}
    carritoItems = orden['get_cart_items']

    for i in carroGuest:
        try:
            carritoItems += carroGuest[i]['cantidad']
            producto = Producto.objects.get(id=i)

            total = (producto.precio * carroGuest[i]['cantidad'])

            orden['get_carrito_total'] += total
            orden['get_cart_items'] += carroGuest[i]['cantidad']

            itemCarro = {
                'producto':{
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': producto.precio,
                    'imageURL': producto.imageURL
                },
                'cantidad': carroGuest[i]['cantidad'],
                'get_total': total,
            }
            items.append(itemCarro)

            if producto.entrega == True:
                orden['despacho'] = True
        except:
            pass

    return{'items':items, 'orden':orden, 'carritoItems':carritoItems}


def carritoData(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
        orden, created = Orden.objects.get_or_create(cliente=cliente, complete=False)
        items = orden.ordenitem_set.all()
        carritoItems = orden.get_cart_items
    else:
        cookieData = cookieCarrito(request)
        carritoItems = cookieData['carritoItems']
        orden = cookieData['orden']
        items = cookieData['items'] 
    
    return{'items':items, 'orden':orden, 'carritoItems':carritoItems}

def ordenGuest(request, data):
        nombre = data['form']['nombre']
        correo = data['form']['email']

        cookieData = cookieCarrito(request)
        items = cookieData['items']

        cliente, created = Cliente.objects.get_or_create(
            correo=correo,
        )
        cliente.nombre = nombre
        cliente.save()

        orden = Orden.objects.create(
            cliente=cliente,
            complete=False,
        )

        for item in items:
            producto = Producto.objects.get(id=item['producto']['id'])
            ordenItem = OrdenItem.objects.create(
                producto=producto,
                orden=orden,
                cantidad=item['cantidad'],
            )
        return cliente, orden
