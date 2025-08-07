from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class UserTests(APITestCase):
    def test_user_registration(self):
        url = reverse('user-register') 
        data = {
            'email': 'test@example.com',
            'username': 'terstin',
            'password': 'strongpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
        
class AuthTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            username='terstin',
            password='testpass123'
        )

    def test_login_jwt(self):
        response = self.client.post('/api/users/login/', {
            'email': 'user@example.com',
            'username': 'terstin',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
class ProjectTests(APITestCase):
    
    def setUp(self):
        # Utilisateur propriétaire
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass123'
        )
        # Autre utilisateur
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass123'
        )
        # Projet existant
        self.project = Project.objects.create(
            title='Projet initial',
            description='Un projet de test',
            owner=self.owner
        )
        self.url_list = '/api/projects/'
        self.url_detail = f'/api/projects/{self.project.id}/'

    def test_create_project_authenticated(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Nouveau projet',
            'description': 'Description du nouveau projet'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().owner, self.owner)

    def test_create_project_unauthenticated(self):
        data = {
            'title': 'Projet non autorisé',
            'description': 'Tentative sans auth'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Projet modifié',
            'description': 'Nouvelle description'
        }
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Projet modifié')

    def test_update_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            'title': 'Hacking du projet',
            'description': 'Je ne suis pas le propriétaire'
        }
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)