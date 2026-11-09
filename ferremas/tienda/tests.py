from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from tienda.models import Rol, UsuarioSistema, Producto, Orden, OrdenItem


class ModelosYLogicaTestCase(TestCase):

    def setUp(self):
        self.rol_cliente = Rol.objects.create(
            nombre_rol="Cliente",
            descripcion_rol="Cliente registrado"
        )
        self.user_auth = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!"
        )

    def test_creacion_usuario_sistema(self):
        usuario_sistema = UsuarioSistema.objects.create(
            usuario=self.user_auth,
            nombre="Juan Pérez",
            correo="testuser@example.com",
            contrasena=self.user_auth.password,
            telefono="+56912345678",
            rol=self.rol_cliente
        )
        self.assertEqual(usuario_sistema.nombre, "Juan Pérez")
        self.assertEqual(usuario_sistema.correo, "testuser@example.com")
        self.assertEqual(usuario_sistema.rol.nombre_rol, "Cliente")

    def test_calculo_dinamico_get_carrito_total(self):
        usuario_sistema = UsuarioSistema.objects.create(
            usuario=self.user_auth,
            nombre="Juan Pérez",
            correo="testuser@example.com",
            contrasena=self.user_auth.password,
            telefono="+56912345678",
            rol=self.rol_cliente
        )

        # 1. Instanciar Producto ($15.000) y Orden
        producto = Producto.objects.create(
            nombre="Taladro Percutor",
            descripcion="Taladro inalámbrico",
            precio=Decimal("15000.00"),
            stock_disp=10,
            entrega=True
        )

        orden = Orden.objects.create(
            usuario=usuario_sistema,
            complete=False
        )

        # 2. Crear OrdenItem con cantidad 3
        OrdenItem.objects.create(
            producto=producto,
            orden=orden,
            cantidad=3
        )

        # 3. Aserción de totales ($15.000 x 3 = $45.000)
        self.assertEqual(orden.get_carrito_total, Decimal("45000.00"))