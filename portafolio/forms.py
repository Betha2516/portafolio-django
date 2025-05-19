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
        # VERIFICAR SI LAS CONTRASEñas son iguales
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
        # guardar el usuario en ambas tablas
        user = User(
            username=self.cleaned_data['correo'],
            first_name=self.cleaned_data['nombre'],
            last_name=self.cleaned_data['apellido'],
            email=self.cleaned_data['correo']
        )
        user.set_password(self.cleaned_data['contraseña'])
        if commit:
            user.save()
            # Agregar el usuario al grupo seleccionado
            grupo = self.cleaned_data['rol']
            user.groups.add(grupo)

            client = super().save(commit=False)
            client.user = user
            if commit:
                client.save()
        return user


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['nombre', 'empresa']