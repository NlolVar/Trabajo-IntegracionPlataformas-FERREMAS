from django.template import context
from django.shortcuts import render
from django.http import JsonResponse
from tienda.models import *
import json, datetime
from tienda.utils import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as django_login, logout
from django.shortcuts import render, redirect
from tienda.forms import (
    CustomUserCreationForm,
    FormularioLogin,
    ProductoForm,
    UsuarioForm,
)
from django.contrib.auth.decorators import user_passes_test

def es_administrador(user):
    if not user.is_authenticated:
        return False
    try:
        return user.usuariosistema.rol.nombre_rol == 'Administrador'
    except:
        return False
    
def herramientaReport(user):
    if not user.is_authenticated:
        return False
    try:
        rol = user.usuariosistema.rol.nombre_rol
        return rol in ('Vendedor', 'Administrador', 'Contador')
    except:
        return False
# Create your views here.


def tienda(request):
    
    data = carritoData(request)

    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']

    productos = Producto.objects.all()
    context = {'productos':productos, 'carritoItems':carritoItems}
    return render(request, 'tienda/tienda.html', context)

def carrito(request):
    
    data = carritoData(request)

    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']

    context = {'items':items, 'orden':orden, 'carritoItems':carritoItems}
    return render(request, 'tienda/carrito.html', context)

def pago(request):
    
    data = carritoData(request)

    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']

    context = {'items':items, 'orden':orden, 'carritoItems':carritoItems}
    return render(request, 'tienda/pago.html', context)

def catalogo(request):
    
    data = carritoData(request)
    carritoItems = data['carritoItems']

    query = request.GET.get('buscar')

    if query:
        productos = Producto.objects.filter(nombre__icontains=query)
    else:
        productos = Producto.objects.all()

    context = {'productos':productos,'carritoItems':carritoItems, 'query':query}
    return render(request, 'tienda/catalogo.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # print('action', action)
    # print('Product', productId)
    if not request.user.is_authenticated:
        return JsonResponse('El usuario no esta logeado.', safe=False, status=401)
    try:
        usuario = request.user.usuariosistema
    except UsuarioSistema.DoesNotExist:
        usuario = UsuarioSistema.objects.create(
            usuario=request.user,
            nombre=request.user.get_full_name() or request.user.username,
            correo=request.user.email,
            contrasena=request.user.password
        )
        return JsonResponse('El usuario no posee un perfil de UsuarioSistema configurado.', safe=False, status=400)
    
    try:
        producto = Producto.objects.get(id=productId)
    except Producto.DoesNotExist:
        return JsonResponse('El producto no existe.', safe=False, status=404)

    
    orden, created = Orden.objects.get_or_create(usuario=usuario, complete=False)
    ordenItem, created = OrdenItem.objects.get_or_create(orden=orden, producto=producto)
    
    if action == 'add':
        ordenItem.cantidad = (ordenItem.cantidad + 1)
    elif action == 'remove':
        ordenItem.cantidad = (ordenItem.cantidad - 1)

    ordenItem.save()

    if ordenItem.cantidad <= 0:
        ordenItem.delete()

    return JsonResponse('producto fue agregado', safe=False)

@csrf_exempt
def processOrder(request):
    transaccion_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        try:
            usuario = request.user.usuariosistema
        except UsuarioSistema.DoesNotExist:
            return JsonResponse('El usuario no posee un perfil de UsuarioSistema configurado.', safe=False, status=400)
        orden, created = Orden.objects.get_or_create(usuario=usuario, complete=False)
        total = float(data['form']['total'])
        orden.transaccion_id = transaccion_id

        if total == float(orden.get_carrito_total):
            orden.complete = True
            orden.save()

        if orden.despacho == True:
            DireccionDespacho.objects.create(
                usuario=usuario,
                orden=orden,
                direccion=data['despacho']['direccion'],
                ciudad=data['despacho']['ciudad'],
                comuna=data['despacho']['comuna'],
                codigo_postal=data['despacho']['codigoPostal']
            )
    else:
        print('Usuario no esta logeado.')

        print('COOKIES', request.COOKIES)

        usuario, orden = ordenGuest(request, data)
        
        total = float(data['form']['total'])
        orden.transaccion_id = transaccion_id

        if total == float(orden.get_carrito_total):
            orden.complete = True
        orden.save()

        if orden.despacho == True:
            DireccionDespacho.objects.create(
                usuario=usuario,
                orden=orden,
                direccion=data['despacho']['direccion'],
                ciudad=data['despacho']['ciudad'],
                comuna=data['despacho']['comuna'],
                codigo_postal=data['despacho']['codigoPostal'],
            )

    return JsonResponse('pago fue enviado...', safe=False)


def login_usuario(request): # Le cambiamos el nombre a la vista para que sea súper claro
    # Si el usuario ya está autenticado, lo mandamos directo a la tienda
    if request.user.is_authenticated:
        return redirect('tienda')

    data = carritoData(request)
    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']

    form = FormularioLogin()
    error_message = None

    if request.method == 'POST':   
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                django_login(request, user) # <--- Aquí usamos el login de Django renombrado
                return redirect('tienda')
        else:
            error_message = "Usuario o contraseña incorrectos."

    context = {
        'form': form,
        'carritoItems': carritoItems,
        'orden': orden,
        'items': items,
        'error_message': error_message
    }
    
    return render(request, 'sesion/login.html', context)

def register(request):
    data = carritoData(request)
    carritoItems = data['carritoItems']
    user_creation_form = CustomUserCreationForm()

    contexto_data = {
        'form': user_creation_form,
        'carritoItems': carritoItems
    }

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        # if user_creation_form.is_valid():
        #     user = user_creation_form.save()
        #     django_login(request, user)
        #     return redirect('tienda')
        # else:
        #     contexto_data['form'] = user_creation_form
        if user_creation_form.is_valid():
            # Esto ahora guarda de forma interna el User de Django Y el UsuarioSistema
            user = user_creation_form.save()

            username = user_creation_form.cleaned_data.get('username')
            password = user_creation_form.cleaned_data.get('password1')
            
            user_authenticated = authenticate(username=username, password=password)
            
            if user_authenticated is not None:
                django_login(request, user_authenticated) # <-- Inicia sesión con la función de Django
                return redirect('tienda')
        else:
            data['form'] = user_creation_form

    return render(request, 'sesion/registro.html', contexto_data)

def productos(request):
    lista_productos = Producto.objects.all()
    data = carritoData(request)

    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']
    context = {
        'productos': lista_productos,
        'carritoItems': carritoItems,
        'orden': orden,
        'items': items
    }

    return render(request, 'productos/index.html', context)

def crearProd(request):
    data = carritoData(request)
    carritoItems = data['carritoItems']

    formulario = ProductoForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('producto')
    
    context = {
        'formulario': formulario,
        'carritoItems': carritoItems
    }
    return render(request, 'productos/crear.html', context)

def editarProd(request, id):
    data = carritoData(request)
    carritoItems = data['carritoItems']

    producto = Producto.objects.get(id=id)
    formulario = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if formulario.is_valid() and request.method == 'POST':
        formulario.save()
        return redirect('producto')
    
    context ={
        'formulario': formulario,
        'carritoItems': carritoItems
    }
    return render(request, 'productos/editar.html', context)

def eliminarProd(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('producto')

@user_passes_test(es_administrador, login_url='login')
def usuario(request):
    lista_usuarios = UsuarioSistema.objects.all()
    data = carritoData(request)

    carritoItems = data['carritoItems']
    orden = data['orden']
    items = data['items']
    context = {
        'usuarios': lista_usuarios,
        'carritoItems': carritoItems,
        'orden': orden,
        'items': items
    }

    return render(request, 'usuarios/indexUser.html', context)

@user_passes_test(es_administrador, login_url='login')
def crearUser(request):
    data = carritoData(request)
    carritoItems = data['carritoItems']

    formulario = UsuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('usuario')
    
    context = {
        'formulario': formulario,
        'carritoItems': carritoItems
    }
    return render(request, 'usuarios/crearUser.html', context)

@user_passes_test(es_administrador, login_url='login')
def editarUser(request, id):
    data = carritoData(request)
    carritoItems = data['carritoItems']

    usuario = UsuarioSistema.objects.get(id=id)
    formulario = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)
    if formulario.is_valid() and request.method == 'POST':
        formulario.save()
        return redirect('usuario')
    
    roles = Rol.objects.all()
    context ={
        'formulario': formulario,
        'carritoItems': carritoItems,
        'roles': roles
    }
    return render(request, 'usuarios/editarUser.html', context)

@user_passes_test(es_administrador, login_url='login')
def eliminarUser(request, id):
    usuario = UsuarioSistema.objects.get(id=id)
    usuario.delete()
    return redirect('usuario')


def logout_usuario(request):
    logout(request)
    return redirect('tienda')

@user_passes_test(herramientaReport, login_url='login')
def reporte(request):
    data = carritoData(request)
    carritoItems = data['carritoItems']
    
    # Obtenemos todas las órdenes, ordenadas por la más reciente
    ordenes = Orden.objects.all().order_by('-fecha_orden')
    
    context = {
        'ordenes': ordenes,
        'carritoItems': carritoItems
    }
    return render(request, 'reporte/indexReporte.html', context)

import csv
from django.http import HttpResponse

@user_passes_test(herramientaReport, login_url='login')
def exportar_reporte(request):
    # Obtenemos las órdenes
    ordenes = Orden.objects.all().order_by('-fecha_orden')
    
    # Creamos la respuesta HTTP con el tipo de contenido CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="reporte_ordenes.csv"'
    
    # Escribimos el CSV
    writer = csv.writer(response, delimiter=';')
    
    # Escribimos el encabezado (Header)
    writer.writerow(['Usuario', 'Correo', 'Producto(s)', 'Direccion de Despacho', 'Precio Total', 'Fecha Orden', 'Completada'])
    
    # Iteramos sobre las órdenes para agregar los datos
    for orden in ordenes:
        # Extraemos los productos
        productos_str = ", ".join([f"{item.producto.nombre} (x{item.cantidad})" for item in orden.ordenitem_set.all()])
        
        # Extraemos las direcciones
        direcciones = orden.direcciondespacho_set.all()
        if direcciones:
            direccion = direcciones.first()
            direccion_str = f"{direccion.direccion}, {direccion.comuna}, {direccion.ciudad}"
        else:
            direccion_str = "Sin despacho / Retiro en tienda"
        
        # Fecha formateada
        fecha_str = orden.fecha_orden.strftime("%d/%m/%Y %H:%M")
        
        # Verificamos si la orden tiene un usuario asignado (puede ser un usuario invitado)
        usuario_nombre = orden.usuario.nombre if orden.usuario else "Usuario Anónimo"
        usuario_correo = orden.usuario.correo if orden.usuario else "Sin correo"

        # Escribimos la fila
        writer.writerow([
            usuario_nombre,
            usuario_correo,
            productos_str,
            direccion_str,
            orden.get_carrito_total,
            fecha_str,
            'Si' if orden.complete else 'No'
        ])
        
    return response