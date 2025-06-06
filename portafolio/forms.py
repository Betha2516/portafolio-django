from django import forms
from django.contrib.auth.models import User
from .models import Client,Project
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

class registro(forms.ModelForm):
    nombre = forms.CharField(max_length=30, required=False)
    apellido = forms.CharField(max_length=30, required=False)
    correo = forms.EmailField()
    celular = forms.CharField(max_length=20) 
    contraseña = forms.CharField(widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, empty_label="Selecciona un rol")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Group.objects.all()
    class Meta:
        model = Client
        fields = []

    def clean(self):
        # Verificación de que las contraseñas sean iguales
        cleaned_data = super().clean()
        password = cleaned_data.get('contraseña')
        confirm_password = cleaned_data.get('confirmar_contraseña')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Contraseña no es la misma")

        return cleaned_data

    # Verificar que el correo aún no haya sido utilizado en la base de datos.
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if User.objects.filter(email=correo).exists():
            raise forms.ValidationError("Correo ya existente")
        return correo

    # Verifica que el celular no haya sido usado en la base de datos
    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if Client.objects.filter(celular=celular).exists():
            raise forms.ValidationError("Celular ya existente")
        return celular

    # Guardar el usuario en la base de datos
    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['correo'],
            first_name=self.cleaned_data['nombre'],
            last_name=self.cleaned_data['apellido'],
            email=self.cleaned_data['correo']
        )
        user.set_password(self.cleaned_data['contraseña'])

        if commit:
            user.save()
            # Agregar al rol definido
            grupo = self.cleaned_data['rol']
            user.groups.add(grupo)

            # Crear el cliente y asignar los datos
            client = super().save(commit=False)
            client.user = user
            client.celular = self.cleaned_data['celular']
            client.save()

        return user

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['nombre', 'empresa', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }
        
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            # Verificar que el archivo que se está subiendo es una imágen
            if not imagen.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError('El archivo debe ser una imagen (PNG, JPG, JPEG o GIF).')
            # Verificar el tamaño para optimización de la aplicación
            if imagen.size > 2 * 1024 * 1024:
                raise forms.ValidationError('El tamaño máximo de la imagen es 2 MB.')
        return imagen
    
class EditUserForm(forms.ModelForm):
    """
    Formulario para la edición de un usuario ya existente desde la vista de administrador.
    """
    first_name = forms.CharField(label='Nombre', max_length=30, required=True)
    last_name = forms.CharField(label='Apellido', max_length=30, required=True)
    email = forms.EmailField(label='Email', required=True)
    celular = forms.CharField(label='Celular', max_length=15, required=True)
    
    # Seleccion del rol del usuario para permitir que el admin lo cambie.
    rol = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Rol',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validación: Verificar que todos los campos tengan datos
        for field_name, field_value in cleaned_data.items():
            if field_value is None or field_value == '':
                raise ValidationError(f"El campo {field_name} es obligatorio.")
        
        # Validación: Verificar que se haya seleccionado un rol
        if 'rol' not in cleaned_data or cleaned_data['rol'] is None:
            raise ValidationError("Debe seleccionar un rol para el usuario.")
            
        return cleaned_data