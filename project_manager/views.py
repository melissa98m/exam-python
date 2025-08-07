from rest_framework import generics, permissions, filters
from django.shortcuts import get_object_or_404
from .models import User, Project
from .serializers import UserSerializer, ProjectSerializer
from .permissions import IsOwnerOrReadOnly
from .pagination import  CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

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

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'id'

