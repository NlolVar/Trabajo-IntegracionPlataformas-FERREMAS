from enum import unique
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Rol(models.Model):
	nombre_rol = models.CharField(max_length=255, unique=True)
	descripcion_rol = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.nombre_rol

class UsuarioSistema(models.Model):
	usuario = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE)
	nombre = models.CharField(max_length=255, null=False)
	correo = models.CharField(max_length=255)
	contrasena = models.CharField(max_length=255, null=False, blank=False)
	telefono = models.CharField(max_length=255)
	rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.nombre

class Producto(models.Model):
	nombre = models.CharField(max_length=200, null=False)
	descripcion = models.CharField(max_length=500, null=True, blank=True)
	precio = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=False)
	stock_disp = models.IntegerField(default=0, null=False)
	entrega = models.BooleanField(default=False, null=False, blank=False)
	image = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.nombre

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = '/static/images/placehold-tienda.png'
		return url

class Orden(models.Model):
	usuario = models.ForeignKey(UsuarioSistema, on_delete=models.SET_NULL, null=True, blank=True)
	fecha_orden = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)
	
	@property
	def get_carrito_total(self):
		orderitems = self.ordenitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.ordenitem_set.all()
		total = sum([item.cantidad for item in orderitems])
		return total 
		
	@property
	def despacho(self):
		despacho = False
		ordenItems = self.ordenitem_set.all()
		for i in ordenItems:
			if i.producto.entrega == True:
				despacho = True
		return despacho

class OrdenItem(models.Model):
	producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
	orden = models.ForeignKey(Orden, on_delete=models.SET_NULL, null=True)
	cantidad = models.IntegerField(default=0, null=True, blank=True)
	fecha_agregada = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.producto.precio * self.cantidad
		return total
	
class DireccionDespacho(models.Model):
	usuario = models.ForeignKey(UsuarioSistema, on_delete=models.SET_NULL, null=True)
	orden = models.ForeignKey(Orden, on_delete=models.SET_NULL, null=True)
	direccion = models.CharField(max_length=200, null=False)
	ciudad = models.CharField(max_length=200, null=False)
	comuna = models.CharField(max_length=200, null=False)
	codigo_postal = models.CharField(max_length=200, null=False)
	fecha_agregada = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.direccion