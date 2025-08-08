from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, Project
from .serializers import UserSerializer, ProjectSerializer
from .permissions import IsOwnerOrReadOnly
from .pagination import CustomPagination

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Créer un utilisateur",
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    @swagger_auto_schema(
        operation_description="Récupérer le profil de l’utilisateur courant",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Mettre à jour le profil de l’utilisateur courant",
        request_body=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement le profil de l’utilisateur courant",
        request_body=UserSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Supprimer le profil de l’utilisateur courant",
        responses={204: 'No Content'}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

# Paramètres de requête documentés pour la liste
title_param = openapi.Parameter(
    'title', openapi.IN_QUERY, description="Filtrer par sous-chaîne du titre",
    type=openapi.TYPE_STRING
)
search_param = openapi.Parameter(
    'search', openapi.IN_QUERY, description="Recherche plein‑texte (SearchFilter) sur title",
    type=openapi.TYPE_STRING
)
ordering_param = openapi.Parameter(
    'ordering', openapi.IN_QUERY,
    description="Tri: 'title' ou 'created_at' (préfixer par '-' pour décroissant)",
    type=openapi.TYPE_STRING
)

class ProjectListCreate(generics.ListCreateAPIView):
    """
    Vue combinée pour lister (avec pagination, tri et filtre par titre)
    et créer des projets.
    """
    serializer_class = ProjectSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['title', 'created_at']
    search_fields = ['owner__id'  , 'title']
    
    def get_queryset(self):
        queryset = Project.objects.all()
        title_query = self.request.query_params.get('title')
        if title_query:
            queryset = queryset.filter(title__icontains=title_query)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    @swagger_auto_schema(
        operation_description="Liste paginée des projets",
        manual_parameters=[title_param, search_param, ordering_param],
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Créer un projet",
        request_body=ProjectSerializer,
        responses={201: ProjectSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'id'
    
    @swagger_auto_schema(responses={200: ProjectSerializer})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ProjectSerializer, responses={200: ProjectSerializer})
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ProjectSerializer, responses={200: ProjectSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

