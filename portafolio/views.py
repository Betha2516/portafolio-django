from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Client, Project, Comment
from .forms import registro
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import permission_required

def home(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            cliente, created = Client.objects.get_or_create(user=request.user)
            comentarios = Comment.objects.all().order_by('-created_at')
            return render(request, "home.html", {'comentarios': comentarios})
        else:
            return render(request, "home.html")
        
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
       
        if user is not None:
            login(request, user)
            messages.success(request, "Inicio sesion correctamente")
            return redirect("home")
        else:
            messages.error(request, "Error al iniciar sesión")
            return redirect("login")
    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "Cerro sesion correctamente")
    return redirect("home")

def register(request):
    fm = registro(request.POST or None)
    fm.fields['rol'].queryset = Group.objects.all()
    if request.method == "POST":
        if fm.is_valid():
            fm.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("login")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    return render(request, "registrarse.html", {"form": fm})

@login_required
@permission_required('portafolio.view_project')
@require_http_methods(["GET"])
def view_project(request):
    query = request.GET.get('q', '')
    projects = Project.objects.all().order_by('nombre')
    if query:
        projects = projects.filter(nombre__icontains=query)
    paginator = Paginator(projects, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'proyectos.html', {'page_obj': page_obj, 'query': query})

@login_required
@permission_required('portafolio.add_project')
@require_http_methods(["GET", "POST"])
def create_project(request):
    if request.method == 'GET':
        return redirect('view_project')
    
    if request.method == 'POST':
        empresa = request.POST.get('empresa', '').strip()
        nombre = request.POST.get('proyecto', '').strip()
        
        # Validación de campos vacíos
        if not empresa or not nombre:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('view_project')

        # Validación de proyecto duplicado
        if Project.objects.filter(empresa=empresa, nombre=nombre).exists():
            messages.error(request, 'Ya existe un proyecto con ese nombre y empresa.')
            return redirect('view_project')
            
        # Crear el proyecto
        project = Project(
            empresa=empresa,
            nombre=nombre
        )
        
        # Manejo de la imagen
        if 'imagen' in request.FILES:
            project.imagen = request.FILES['imagen']
        
        project.save()
        messages.success(request, 'Proyecto agregado exitosamente')
        return redirect('view_project')
    return HttpResponse("Método no permitido", status=405)


@login_required
@permission_required('portafolio.delete_project')
@require_http_methods(["POST"])
def delete_project(request, proyecto_id):
    try:
        proyecto = Project.objects.get(id=proyecto_id)
        messages.success(request, 'Proyecto eliminado exitosamente')
        proyecto.delete()
        return JsonResponse({'status': 'success', 'message': 'Proyecto eliminado exitosamente'})
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El proyecto no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al eliminar el proyecto: {str(e)}'}, status=500)

@login_required
def search_projects(request):
    query = request.GET.get("q", "")
    proyectos = Project.objects.filter(nombre__icontains=query)
    data = []
    for proyecto in proyectos:
        data.append({
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "empresa": proyecto.empresa,
            "perm_delete": request.user.has_perm('portafolio.delete_project'),
            "perm_edit": request.user.has_perm('portafolio.change_project')
        })
    return JsonResponse({"proyectos": data})

@login_required
@require_http_methods(["GET", "POST"])
@permission_required('portafolio.change_project')
def edit_project(request, proyecto_id):
    try:
        project = Project.objects.get(id=proyecto_id)
        if request.method == 'POST':
            project.nombre = request.POST.get('nombre')
            project.empresa = request.POST.get('empresa')
            
            # Manejo de la imagen
            if 'imagen' in request.FILES:
                # Si se proporciona una nueva imagen, actualizar
                project.imagen = request.FILES['imagen']
            
            project.save()
            messages.success(request, 'Proyecto actualizado exitosamente')
            return redirect('view_project')
        return redirect('view_project')
    except Project.DoesNotExist:
        messages.error(request, 'El proyecto no existe')
        return redirect('view_project')

@login_required
@require_http_methods(['POST'])
@permission_required('portafolio.add_comment', raise_exception=True)
def create_commit(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    content = request.POST.get("content")
    rating = request.POST.get("rating") 

    if not content:
        messages.error(request, "No se realizó el comentario: falta el contenido.")
        return redirect('view_project') 

    try:
        rating = int(rating) if rating else None
        if rating and (rating < 1 or rating > 5):
            messages.error(request, "La calificación debe estar entre 1 y 5.")
            return redirect('view_project')
    except ValueError:
        messages.error(request, "La calificación proporcionada no es válida.")
        return redirect('view_project')

    Comment.objects.create(
        project=project,
        author=request.user,
        content=content,
        rating=rating
    )
    messages.success(request, "Comentario creado correctamente.")
    return redirect('view_project')

@login_required
def perfil_usuario(request):
    usuario = request.user
    contexto = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/perfil.html', contexto)

@login_required
@require_http_methods(["GET"])
def perfil_usuario(request):
    try:
        cliente = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        cliente = None
    
    context = {
        'usuario': request.user,
        'cliente': cliente,
    }
    
    return render(request, 'perfil_usuario.html', context)