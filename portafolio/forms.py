from django import forms
from django.contrib.auth.models import User
from .models import Client,Project
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django.contrib.auth.models import Group

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

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if User.objects.filter(email=correo).exists():
            raise forms.ValidationError("Correo ya existente")
        return correo

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if Client.objects.filter(celular=celular).exists():
            raise forms.ValidationError("Celular ya existente")
        return celular

    def save(self, commit=True):
        # Guardar el usuario en la tabla User
        user = User(
            username=self.cleaned_data['correo'],
            first_name=self.cleaned_data['nombre'],
            last_name=self.cleaned_data['apellido'],
            email=self.cleaned_data['correo']
        )
        user.set_password(self.cleaned_data['contraseña'])

        if commit:
            user.save()
            # Agregar al grupo
            grupo = self.cleaned_data['rol']
            user.groups.add(grupo)

            # Crear instancia de Client y asignar campos manualmente
            client = super().save(commit=False)
            client.user = user
            client.celular = self.cleaned_data['celular']  # <- Asignación manual del celular
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
            # Validar el tipo de archivo
            if not imagen.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError('El archivo debe ser una imagen (PNG, JPG, JPEG o GIF).')
            # Validar el tamaño (máximo 2 MB)
            if imagen.size > 2 * 1024 * 1024:
                raise forms.ValidationError('El tamaño máximo de la imagen es 2 MB.')
        return imagen
    
class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombre', max_length=30, required=False)
    last_name = forms.CharField(label='Apellido', max_length=30, required=False)
    email = forms.EmailField(label='Email', required=True)
    celular = forms.CharField(label='Celular', max_length=15, required=False)
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label='Roles',
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')