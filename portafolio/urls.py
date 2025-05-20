from django.urls import path
from . import views

urlpatterns = [
        path("",views.home, name="home" ),
        path("login/",views.user_login, name="login"),
        path("logout/", views.logout_user, name="logout"),
        path("register/",views.register, name="register"),
        path('view-project/', views.view_project, name='view_project'),
        path('create-project/', views.create_project, name='create_project'),
        path('edit-project/<int:proyecto_id>/', views.edit_project, name='edit_project'),
        path('delete-project/<int:proyecto_id>/', views.delete_project, name='delete_project'),
        path('search_projects/', views.search_projects, name='search_projects'), 
        path('create-commit/<int:project_id>/', views.create_commit, name='create_commit'),
       
]
