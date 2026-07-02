from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from tienda.models import Rol, UsuarioSistema, Producto

class FormularioLogin(AuthenticationForm):
    pass

class CustomUserCreationForm(UserCreationForm):
    nombre = forms.CharField(required=True, label="Usuario")
    email = forms.EmailField(required=True, label="Correo")
    telefono = forms.CharField(required=True, label="Teléfono")

    field_order = ['nombre','email', 'telefono', 'password1', 'password2']
    
    class Meta:
        model = User
        # Mantenemos 'username' y 'email' que son los campos reales del modelo User de Django
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ocultamos el campo 'username' original para que el usuario solo vea "nombre" en el HTML
        if 'username' in self.fields:
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].required = False

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        
        # El valor de 'nombre' alimentará al 'username' obligatorio de Django
        if nombre:
            cleaned_data['username'] = nombre
            self.instance.username = nombre
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

# AQUÍ OCURRE LA MAGIA: Personalizamos el guardado en forms.py
    def save(self, commit=True):
        # 1. Guardamos primero el usuario en la tabla User de Django para obtener las credenciales seguras
        user = super().save(commit=commit)
        
        # 2. Buscamos el rol "cliente" de forma segura en tu tabla personalizada 'Rol'
        # Usamos __iexact para que coincida sin importar mayúsculas/minúsculas ("cliente", "Cliente", etc.)
        rol_por_defecto = Rol.objects.filter(nombre_rol__iexact="cliente").first() 

        # 3. Creamos el perfil en tu tabla UsuarioSistema con el rol asignado
        UsuarioSistema.objects.create(
            usuario=user,                                      # Enlace OneToOne
            nombre=self.cleaned_data.get('nombre'),
            correo=self.cleaned_data.get('email'),
            contrasena=user.password,                          # Guarda la contraseña ya encriptada por Django
            telefono=self.cleaned_data.get('telefono'),
            rol=rol_por_defecto                                # Asigna el rol obtenido
        )
        return user
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = UsuarioSistema
        fields = '__all__'