from django.contrib import admin

# Register your models here.

from tienda.models import *

admin.site.register(Rol)
admin.site.register(UsuarioSistema)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(OrdenItem)
admin.site.register(DireccionDespacho)