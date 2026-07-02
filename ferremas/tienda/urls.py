from django.urls import path
from tienda import views

urlpatterns = [
        #Leave as empty string for base url
	path('', views.tienda, name="tienda"),
	path('carrito/', views.carrito, name="carrito"),
	path('pago/', views.pago, name="pago"),
    path('catalogo/', views.catalogo, name="catalogo"),
	path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('login/', views.login_usuario, name="login"),
	path('registro/', views.register, name="registro"),
    path('productos/', views.productos, name="producto"),
    path('productos/crear', views.crearProd, name="crear"),
    path('eliminar/<int:id>', views.eliminarProd, name="eliminar"),
    path('productos/editar/<int:id>', views.editarProd, name="editar"),
    path('usuarios/', views.usuario, name="usuario"),
    path('usuarios/crear', views.crearUser, name="crearUser"),
    path('eliminarUser/<int:id>', views.eliminarUser, name="eliminarUser"),
    path('usuarios/editar/<int:id>', views.editarUser, name="editarUser"),
    path('logout/', views.logout_usuario, name="logout")
]