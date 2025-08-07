from django.urls import path
from . import views

urlpatterns = [
    path('users/register/', views.RegisterUser.as_view(), name='user-register'),
    path('users/<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('projects/', views.ProjectListCreate.as_view(), name='project-list'),
    path('projects/<int:id>/<str:username>/', views.ProjectDetail.as_view(), name='project-detail'),
]
