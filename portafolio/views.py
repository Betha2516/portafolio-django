from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Client, Project, Comment
from .forms import registro
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import get_user_model
from .forms import EditUserForm

User = get_user_model()

# Renderizar el home, muestra comentarios si el usuario está autenticado
def home(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            cliente, created = Client.objects.get_or_create(user=request.user)

            # Obtiene comentarios para mostrarlo al final de la página
            comentarios = Comment.objects.all().order_by('-created_at')
            return render(request, "home.html", {'comentarios': comentarios})
        else:
            return render(request, "home.html")
        
# Vista para registrar nuevos usuarios
def register(request):
    fm = registro(request.POST or None)

    # Limita los roles que se pueden asignar durante el registro
    fm.fields['rol'].queryset = Group.objects.all()

    if request.method == "POST":
        if fm.is_valid():
            fm.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("login")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    
    return render(request, "registrarse.html", {"form": fm})
        
# Vista para inicio de sesión de usuarios
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Verifica las credenciales del usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio sesion correctamente")
            return redirect("home")
        else:
            messages.error(request, "Error al iniciar sesión")
            return redirect("login")
    
    return render(request, "login.html")

# Cerrar sesión del usuario
def logout_user(request):
    logout(request)
    messages.success(request, "Cerro sesion correctamente")
    return redirect("home")

# Vista de proyectos con paginación, se debe contar con el permiso de portafolio.view_project para poder usarla
@login_required
@permission_required('portafolio.view_project')
@require_http_methods(["GET"])
def view_project(request):
    query = request.GET.get('q', '')

    projects = Project.objects.all().order_by('nombre')

    # Filtro por nombre
    if query:
        projects = projects.filter(nombre__icontains=query)

    # Solo mostrar 20 proyectos por página
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'proyectos.html', {'page_obj': page_obj, 'query': query})

# Vista para crear un proyecto, solo se puede acceder con el permiso portafolio.add_project
@login_required
@permission_required('portafolio.add_project')
@require_http_methods(["GET", "POST"])
def create_project(request):
    if request.method == 'GET':
        return redirect('view_project')
    
    if request.method == 'POST':
        empresa = request.POST.get('empresa', '').strip()
        nombre = request.POST.get('proyecto', '').strip()
        
        # Validar que ambos campos estan presentes
        if not empresa or not nombre:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('view_project')

        # Validar que no se repitan combinaciones de proyecto + empresa
        if Project.objects.filter(empresa=empresa, nombre=nombre).exists():
            messages.error(request, 'Ya existe un proyecto con ese nombre y empresa.')
            return redirect('view_project')
            
        project = Project(empresa=empresa, nombre=nombre)
        
        # Guardar en el modelo del proyecto la imágen subida
        if 'imagen' in request.FILES:
            project.imagen = request.FILES['imagen']
        
        project.save()

        messages.success(request, 'Proyecto agregado exitosamente')
        return redirect('view_project')
    
    return HttpResponse("Método no permitido", status=405)

# Vista para eliminar un proyecto, necesita del permiso portafolio.delete_project
@login_required
@permission_required('portafolio.delete_project')
@require_http_methods(["POST"])
def delete_project(request, proyecto_id):
    try:
        proyecto = Project.objects.get(id=proyecto_id)

        proyecto.delete()
        messages.success(request, 'Proyecto eliminado exitosamente')

        # Retornar un mensaje de éxito en formato JSON
        return JsonResponse({'status': 'success', 'message': 'Proyecto eliminado exitosamente'})
    
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El proyecto no existe'}, status=404)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al eliminar el proyecto: {str(e)}'}, status=500)

# Vista para buscar proyectos por nombre
@login_required
def search_projects(request):
    query = request.GET.get("q", "")
    proyectos = Project.objects.filter(nombre__icontains=query)

    data = []
    for proyecto in proyectos:
        # Soporte de los botones condicionales
        data.append({
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "empresa": proyecto.empresa,
            "perm_delete": request.user.has_perm('portafolio.delete_project'),
            "perm_edit": request.user.has_perm('portafolio.change_project')
        })

    return JsonResponse({"proyectos": data})

# Vista para editar un proyecto existente, necesita que el usuario tenga el permiso portafolio.change_project
@login_required
@require_http_methods(["GET", "POST"])
@permission_required('portafolio.change_project')
def edit_project(request, proyecto_id):
    try:
        project = Project.objects.get(id=proyecto_id)

        if request.method == 'POST':
            project.nombre = request.POST.get('nombre')
            project.empresa = request.POST.get('empresa')

            # Reemplazar por la imágen cargada
            if 'imagen' in request.FILES:
                project.imagen = request.FILES['imagen']

            project.save()
            messages.success(request, 'Proyecto actualizado exitosamente')
            return redirect('view_project')

        return redirect('view_project')

    except Project.DoesNotExist:
        messages.error(request, 'El proyecto no existe')
        return redirect('view_project')

# Vista para crear un comentario en un proyecto, necesita que el usuario tenga el permiso portafolio.add_comment
@login_required
@require_http_methods(['POST'])
@permission_required('portafolio.add_comment', raise_exception=True)
def create_commit(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    content = request.POST.get("content")
    rating = request.POST.get("rating") 

    if not content:
        # Validar que el contenido no esté vacío
        messages.error(request, "No se realizó el comentario: falta el contenido.")
        return redirect('view_project') 

    try:
        rating = int(rating) if rating else None

        # Validar que el rating esté dentro del rango permitido
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

# Vista para mostrar el perfil del usuario
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

# Vista para obtener la lista de usuarios que será mostrada en la tabla de admin, se necesita del permiso auth.view_user
@login_required
@permission_required('auth.view_user')
@require_http_methods(["GET"])
def lista_usuarios(request):
    # Filtrado
    query = request.GET.get('q', '')
    
    # Ordenar por ID (a pesar de que el ID no se muestra en la tabla)
    usuarios = User.objects.all().order_by('id').prefetch_related('groups')
    
    # Filtros de búsqueda
    if query:
        usuarios = usuarios.filter(
            username__icontains=query
        ) | usuarios.filter(
            first_name__icontains=query
        ) | usuarios.filter(
            last_name__icontains=query
        ) | usuarios.filter(
            email__icontains=query
        )
        
    # Solo mostrar 10 usuarios por página
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    groups = Group.objects.all()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'groups': groups
    }
    
    return render(request, 'lista_usuarios.html', context)

# Vista para borrar un usuario, requiere del permiso auth.delete_user
@login_required
@permission_required('auth.delete_user', raise_exception=True)
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.delete()
        return HttpResponse(status=204)
    return HttpResponse(status=405)

# Vista para editar un usuario, requiere del permiso auth.change_user
@login_required
@permission_required('auth.change_user', raise_exception=True)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            
            rol_seleccionado = form.cleaned_data.get('rol')
            # Quitar todos los roles que tenga el usuario para asignarle el nuevo
            user.groups.clear()
            # Asignar nuevo rol
            if rol_seleccionado:
                user.groups.add(rol_seleccionado)
            
            user.save()
            
            # Actualizar o crear cliente 
            celular = form.cleaned_data.get('celular')
            cliente, created = Client.objects.get_or_create(user=user)
            cliente.celular = celular
            cliente.save()
            
            messages.success(request, f"Usuario {user.username} actualizado correctamente.")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f"Usuario {user.username} actualizado correctamente."})
            else:
                messages.success(request, f"Usuario {user.username} actualizado correctamente.")
                return redirect('lista_usuarios')

        else:
            # Si hay errores de validación
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: error for field, error in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        initial_data = {
            'username': usuario.username,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'email': usuario.email,
        }
        
        # Añadir celular a la data inicial si el cliente ya existe y está asociado a un user
        try:
            if hasattr(usuario, 'client') and usuario.client:
                initial_data['celular'] = usuario.client.celular
        except Client.DoesNotExist:
            pass
            
        # Establecer el rol del usuario en initial data
        if usuario.groups.exists():
            initial_data['rol'] = usuario.groups.first()
            
        form = EditUserForm(initial=initial_data, instance=usuario)
    
    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})