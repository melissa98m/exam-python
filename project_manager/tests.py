from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Project
from math import ceil

User = get_user_model()


#  Couleurs & helpers logs
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def ok(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def fail(msg, extra=None):
    if extra is not None:
        print(f"{RED}✗ {msg} → {extra}{RESET}")
    else:
        print(f"{RED}✗ {msg}{RESET}")

def info(msg):
    print(f"{BLUE}• {msg}{RESET}")
    
# Test registration 

class UserTests(APITestCase):
    def test_user_registration(self):
        url = reverse('user-register')
        data = {'email': 'test@example.com', 'username': 'terstin', 'password': 'strongpassword123'}
        info(f"POST {url} with {data}")
        response = self.client.post(url, data, format='json')
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_201_CREATED:
            ok("User registration returned 201")
        else:
            fail("User registration did not return 201", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = User.objects.count()
        if count == 1:
            ok("Exactly 1 user in database")
        else:
            fail("Unexpected users count", count)
        self.assertEqual(count, 1)

        email = User.objects.first().email
        if email == 'test@example.com':
            ok("Registered user email matches")
        else:
            fail("Registered user email mismatch", email)
        self.assertEqual(email, 'test@example.com')


# Test auth
class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='terstin',
            password='testpass123'
        )

    def test_login_jwt(self):
        url = '/api/users/login/'
        payload = {'username': 'terstin', 'password': 'testpass123'}
        info(f"POST {url} with {payload}")
        response = self.client.post(url, payload, format='json')
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == 200:
            ok("JWT login returned 200")
        else:
            fail("JWT login did not return 200", response.status_code)
        self.assertEqual(response.status_code, 200)

        has_access = 'access' in response.data
        has_refresh = 'refresh' in response.data
        if has_access and has_refresh:
            ok("JWT tokens present (access & refresh)")
        else:
            fail("Missing JWT tokens", response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

#Test permission owner read only
class PermissionOwnerReadOnlyTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='ownp', email='ownp@example.com', password='pass123')
        self.other = User.objects.create_user(username='othp', email='othp@example.com', password='pass123')
        self.project = Project.objects.create(title='Perm Proj', description='x', owner=self.owner)
        self.url_detail = reverse('project-list') + f"{self.project.id}/"

    def test_safe_method_allowed_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        info(f"GET {self.url_detail} en tant que non-propriétaire")
        resp = self.client.get(self.url_detail)
        if resp.status_code == 200:
            ok("GET autorisé pour non-propriétaire (SAFE_METHODS)")
        else:
            fail("GET interdit pour non-propriétaire", resp.status_code)
        self.assertEqual(resp.status_code, 200)

    def test_unsafe_method_forbidden_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        info(f"PUT {self.url_detail} en tant que non-propriétaire")
        resp = self.client.put(self.url_detail, {'title': 'hack', 'description': 'hack'})
        if resp.status_code == 403:
            ok("PUT interdit pour non-propriétaire")
        else:
            fail("PUT accepté pour non-propriétaire", resp.status_code)
        self.assertEqual(resp.status_code, 403)
  
#Test user detail      
class UserDetailTests(APITestCase):
    def setUp(self):
        self.me = User.objects.create_user(username='meuser', email='me@example.com', password='pass123')

    def test_get_own_profile_ignores_lookup_and_returns_request_user(self):
        self.client.force_authenticate(user=self.me)
        url = reverse('user-detail', kwargs={'username': 'someone-else'})
        info(f"GET {url} en étant connecté comme {self.me.username}")
        resp = self.client.get(url)
        info(f"→ status={resp.status_code}, data={resp.data}")
        if resp.status_code == 200 and resp.data['username'] == 'meuser':
            ok("get_object() renvoie bien l'utilisateur connecté")
        else:
            fail("get_object() ne renvoie pas le bon utilisateur", resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'meuser')


# Test project model (CRUD)
class ProjectTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass123')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='pass123')
        self.project = Project.objects.create(title='Projet initial', description='Un projet de test', owner=self.owner)
        self.url_list = reverse('project-list')               # "/api/projects/"
        self.url_detail = f"{self.url_list}{self.project.id}/"  # "/api/projects/<id>/"

    def test_create_project_authenticated(self):
        self.client.force_authenticate(user=self.owner)
        data = {'title': 'Nouveau projet', 'description': 'Description du nouveau projet'}
        info(f"POST {self.url_list} (auth as owner) with {data}")
        response = self.client.post(self.url_list, data)
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_201_CREATED:
            ok("Create project (auth) returned 201")
        else:
            fail("Create project (auth) did not return 201", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_unauthenticated(self):
        data = {'title': 'Projet non autorisé', 'description': 'Tentative sans auth'}
        info(f"POST {self.url_list} (unauth) with {data}")
        response = self.client.post(self.url_list, data)
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            ok("Create project (unauth) returned 401")
        else:
            fail("Create project (unauth) did not return 401", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {'title': 'Projet modifié', 'description': 'Nouvelle description'}
        info(f"PUT {self.url_detail} (as owner) with {data}")
        response = self.client.put(self.url_detail, data)
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_200_OK:
            ok("Update by owner returned 200")
        else:
            fail("Update by owner did not return 200", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacking du projet', 'description': 'Je ne suis pas le propriétaire'}
        info(f"PUT {self.url_detail} (as other) with {data}")
        response = self.client.put(self.url_detail, data)
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_403_FORBIDDEN:
            ok("Update by non-owner correctly forbidden (403)")
        else:
            fail("Update by non-owner should be 403", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        info(f"DELETE {self.url_detail} (as owner)")
        response = self.client.delete(self.url_detail)
        info(f"→ status={response.status_code}")

        if response.status_code == status.HTTP_204_NO_CONTENT:
            ok("Delete by owner returned 204")
        else:
            fail("Delete by owner did not return 204", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        info(f"DELETE {self.url_detail} (as other)")
        response = self.client.delete(self.url_detail)
        info(f"→ status={response.status_code}, data={getattr(response, 'data', None)}")

        if response.status_code == status.HTTP_403_FORBIDDEN:
            ok("Delete by non-owner correctly forbidden (403)")
        else:
            fail("Delete by non-owner should be 403", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#Test string in model 
class ProjectModelStrTests(APITestCase):
    def test_str_returns_title(self):
        u = User.objects.create_user(username='u1', email='u1@example.com', password='pass123')
        p = Project.objects.create(title='Mon Titre', description='d', owner=u)
        info(f"__str__ du projet → {str(p)}")
        if str(p) == 'Mon Titre':
            ok("__str__ renvoie bien le titre")
        else:
            fail("__str__ ne renvoie pas le bon titre", str(p))
        self.assertEqual(str(p), 'Mon Titre')      

#Test project filter
class ProjectFilterTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='ownerf', email='ownerf@example.com', password='pass123')
        self.client.force_authenticate(user=self.owner)
        Project.objects.create(title='Django Pro', description='A', owner=self.owner)
        Project.objects.create(title='React App', description='B', owner=self.owner)
        self.url_list = reverse('project-list')

    def test_filter_by_title_param(self):
        info(f"GET {self.url_list}?title=Django → Filtre par titre")
        resp = self.client.get(self.url_list, {'title': 'Django'})
        info(f"→ status={resp.status_code}, titles={[p['title'] for p in resp.data['results']]}")
        if resp.status_code == 200 and all('Django' in t for t in [p['title'] for p in resp.data['results']]):
            ok("Filtrage par titre fonctionne")
        else:
            fail("Filtrage par titre ne fonctionne pas", resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(all('Django' in t for t in [p['title'] for p in resp.data['results']]))

 
 # Test pagination project       
class ProjectPaginationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass123')
        self.client.force_authenticate(user=self.owner)
        Project.objects.bulk_create([
            Project(title=f'Projet {i}', description='desc', owner=self.owner)
            for i in range(1, 8)  
        ])
        self.url_list = reverse('project-list') 

    def test_pagination_default_page_1(self):
        response = self.client.get(self.url_list)
        info(f"GET {self.url_list} → status={response.status_code}")
        if response.status_code == status.HTTP_200_OK:
            ok("Pagination page 1 returned 200")
        else:
            fail("Pagination page 1 did not return 200", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key in ['total_count', 'total_pages', 'current_page', 'next', 'previous', 'results']:
            if key in response.data:
                ok(f"Key '{key}' present in response")
            else:
                fail(f"Missing key '{key}' in response")
            self.assertIn(key, response.data)

        self.assertEqual(response.data['total_count'], 7)
        self.assertEqual(response.data['total_pages'], ceil(7 / 2))  
        self.assertEqual(response.data['current_page'], 1)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)

    def test_pagination_page_2(self):
        response = self.client.get(self.url_list, {'page': 2})
        info(f"GET {self.url_list}?page=2 → status={response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_page'], 2)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)

    def test_pagination_with_page_size_override(self):
        response = self.client.get(self.url_list, {'page_size': 3})
        info(f"GET {self.url_list}?page_size=3 → status={response.status_code}")
        if len(response.data['results']) == 3:
            ok("page_size override respected (3)")
        else:
            fail("page_size override mismatch", len(response.data['results']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_pages'], ceil(7 / 3))
        self.assertEqual(response.data['current_page'], 1)
        self.assertEqual(len(response.data['results']), 3)

    def test_pagination_last_page_counts(self):
        response = self.client.get(self.url_list, {'page_size': 3, 'page': 3})
        info(f"GET {self.url_list}?page_size=3&page=3 → status={response.status_code}")
        if len(response.data['results']) == 1:
            ok("last page size is 1 as expected")
        else:
            fail("last page size mismatch", len(response.data['results']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_page'], 3)
        self.assertEqual(len(response.data['results']), 1)


# Test pagination max 
class ProjectPaginationMaxPageSizeTests(APITestCase):
    
    def setUp(self):
        self.owner = User.objects.create_user(username='owner2', email='owner2@example.com', password='pass123')
        self.client.force_authenticate(user=self.owner)
        Project.objects.bulk_create([
            Project(title=f'Projet Cap {i}', description='desc', owner=self.owner)
            for i in range(1, 56)  
        ])
        self.url_list = reverse('project-list')

    def test_page_size_capped_to_max_50(self):
        response = self.client.get(self.url_list, {'page_size': 999})
        info(f"GET {self.url_list}?page_size=999 → status={response.status_code}")
        size = len(response.data['results'])
        if size == 50:
            ok("max_page_size cap applied (50)")
        else:
            fail("max_page_size cap not applied", size)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(size, 50)

        response2 = self.client.get(self.url_list, {'page_size': 999, 'page': 2})
        info(f"GET {self.url_list}?page_size=999&page=2 → status={response2.status_code}")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['results']), 5)
        self.assertIsNone(response2.data['next'])
        self.assertIsNotNone(response2.data['previous'])

#Test serializer of project
class ProjectSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='suser', email='suser@example.com', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.url_list = reverse('project-list')

    def test_owner_is_read_only_on_create(self):
        payload = {'title': 'S Proj', 'description': 'desc', 'owner': 9999}
        info(f"POST {self.url_list} avec owner forcé={payload['owner']}")
        resp = self.client.post(self.url_list, payload, format='json')
        if resp.status_code == 201 and resp.data['owner'] == self.user.id:
            ok("owner ignoré lors de la création, prend l'utilisateur connecté")
        else:
            fail("owner non ignoré ou mauvais status", resp.data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['owner'], self.user.id)

    def test_validation_title_required(self):
        info(f"POST {self.url_list} sans title")
        resp = self.client.post(self.url_list, {'description': 'no title'}, format='json')
        if resp.status_code == 400 and 'title' in resp.data:
            ok("Validation title obligatoire fonctionne")
        else:
            fail("Validation title obligatoire échoue", resp.data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('title', resp.data)

    def test_update_does_not_allow_owner_change(self):
        create = self.client.post(self.url_list, {'title': 'Fix', 'description': 'x'}, format='json')
        detail_url = f"{self.url_list}{create.data['id']}/"
        info(f"PATCH {detail_url} pour changer owner")
        resp = self.client.patch(detail_url, {'owner': None}, format='json')
        if resp.status_code == 200 and resp.data['owner'] == self.user.id:
            ok("owner inchangé après update")
        else:
            fail("owner modifié après update", resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['owner'], self.user.id)


#Test search an order in project
class ProjectSearchOrderTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='ord', email='ord@example.com', password='pass123')
        self.client.force_authenticate(user=self.u)
        Project.objects.bulk_create([
            Project(title='Alpha', description='d', owner=self.u),
            Project(title='Beta', description='d', owner=self.u),
            Project(title='Gamma', description='d', owner=self.u),
        ])
        self.url_list = reverse('project-list')

    def test_search_by_title(self):
        info(f"GET {self.url_list}?search=Beta")
        resp = self.client.get(self.url_list, {'search': 'Beta'})
        titles = [r['title'] for r in resp.data['results']]
        if 'Beta' in titles:
            ok("Recherche par title fonctionne")
        else:
            fail("Recherche par title ne fonctionne pas", titles)
        self.assertIn('Beta', titles)

    def test_ordering_by_title_desc(self):
        info(f"GET {self.url_list}?ordering=-title")
        resp = self.client.get(self.url_list, {'ordering': '-title'})
        titles = [r['title'] for r in resp.data['results']]
        if titles and titles[0] >= titles[-1]:
            ok("Tri descendant par title fonctionne")
        else:
            fail("Tri descendant par title échoue", titles)
        self.assertGreaterEqual(titles[0], titles[-1])