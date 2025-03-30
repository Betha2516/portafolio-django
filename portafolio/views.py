from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Client
from .forms import registro
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

def user_login(request):
    if(request.method == "POST"):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            messages.success(request,"Sesion Iniciada correctamente")
            return redirect("login")
        else:
            messages.error(request,"Error al iniciar sesion")
            return redirect("login")
        
    return render(request,"login.html")

def logout_user(request):
    logout(request)
    messages.success(request, "Cerro sesion correctamente")
    return redirect("home")

def registrarse(request):
    fm = registro(request.POST or None)
    if request.method == "POST":
        if fm.is_valid():
            fm.save()
            return redirect("login")

    return render(request, "registrarse.html", {"form": fm})

def home(request):
    # Verificar si el cliente existe para el usuario actual
    if request.user.is_authenticated:
        cliente, created = Client.objects.get_or_create(user=request.user)

        return render(request, "home.html")
    else:
        # Si el usuario no está autenticado, renderizar el template sin el total de ingresos
        return render(request, "home.html")
