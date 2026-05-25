from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(OrdenItem)
admin.site.register(DireccionDespacho)