from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('users/register/', views.RegisterUser.as_view(), name='user-register'),
    path('users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('projects/', views.ProjectListCreate.as_view(), name='project-list'),
    path('projects/<int:id>/', views.ProjectDetail.as_view(), name='project-detail'),
]
