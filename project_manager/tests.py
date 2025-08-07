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
        print(f"[TEST] Registering user with: {data}")
        response = self.client.post(url, data, format='json')
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='terstin',
            password='testpass123'
        )

    def test_login_jwt(self):
        data = {
            'username': 'terstin',
            'password': 'testpass123'
        }
        print(f"[TEST] Logging in with: {data}")
        response = self.client.post('/api/users/login/', data, format='json')
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class ProjectTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass123'
        )
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
        print(f"[TEST] Create project (auth): {data}")
        response = self.client.post(self.url_list, data)
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_unauthenticated(self):
        data = {
            'title': 'Projet non autorisé',
            'description': 'Tentative sans auth'
        }
        print(f"[TEST] Create project (unauth): {data}")
        response = self.client.post(self.url_list, data)
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Projet modifié',
            'description': 'Nouvelle description'
        }
        print(f"[TEST] Update project by owner: {data}")
        response = self.client.put(self.url_detail, data)
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            'title': 'Hacking du projet',
            'description': 'Je ne suis pas le propriétaire'
        }
        print(f"[TEST] Update project by non-owner: {data}")
        response = self.client.put(self.url_detail, data)
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        print(f"[TEST] Delete project by owner")
        response = self.client.delete(self.url_detail)
        print(f"[RESPONSE] Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        print(f"[TEST] Delete project by non-owner")
        response = self.client.delete(self.url_detail)
        print(f"[RESPONSE] Status: {response.status_code}, Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
