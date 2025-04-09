from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Client
from .models import Project
from .forms import registro
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, "home.html", {"inicio_exitoso": True})
        else:
            messages.error(request, "Error al iniciar sesión")
            return redirect("login")
    return render(request, "login.html")


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

from django.shortcuts import render, redirect
from .models import Project

from django.shortcuts import render, redirect
from .models import Project

def proyectos_view(request):
    if request.method == 'POST':
        empresa = request.POST.get('empresa')
        nombre = request.POST.get('proyecto')
        if empresa and nombre:
            Project.objects.create(empresa=empresa, nombre=nombre)
            return redirect('proyectos_view')

    proyectos = Project.objects.all()
    return render(request, 'proyectos.html', {'proyectos': proyectos})

from django.http import JsonResponse

def eliminar_proyecto(request, proyecto_id):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            proyecto = Project.objects.get(id=proyecto_id)
            proyecto.delete()
            return JsonResponse({"success": True})
        except Project.DoesNotExist:
            return JsonResponse({"success": False, "error": "Proyecto no encontrado."})
    return JsonResponse({"success": False, "error": "Método no permitido o no autenticado."})

def buscar_proyectos(request):
    query = request.GET.get("q", "")
    proyectos = Project.objects.filter(nombre__icontains=query)
    data = []
    for proyecto in proyectos:
        data.append({
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "empresa": proyecto.empresa
        })
    return JsonResponse({"proyectos": data})

