[![Python 3.12.3+](https://img.shields.io/badge/Python-3.12.3%2B-a6e3a1?labelColor=45475a)](https://docs.python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-cba6f7.svg?labelColor=45475a)](LICENSE)
[![codecov](https://codecov.io/gh/melissa98m/exam-python/graph/badge.svg?token=L1MPWRJM6O)](https://codecov.io/gh/melissa98m/exam-python)
# 🧪 Exam - Gestion de projets collaboratifs avec Django & DRF

Ce projet est une API REST construite avec Django et Django REST Framework, permettant de gérer des utilisateurs et leurs projets. Il inclut l'authentification JWT, la pagination, la recherche, le filtrage et un déploiement prêt via Docker.

---

## 🚀 Fonctionnalités principales

- Enregistrement d'utilisateurs (`/api/users/register/`)
- Connexion avec JWT (`/api/users/login/`)
- Rafraîchissement de tokens (`/api/users/token/refresh/`)
- Création, modification, suppression de projets
- API REST sécurisée avec des permissions personnalisées
- Filtres : recherche, tri, pagination
- Base de données SQLite pour le développement
- Docker & docker-compose pour l'exécution

---

## 🐳 Lancement rapide avec Docker

```bash
docker-compose up --build
``` 
Accès à l'API :

```bash
http://localhost:8000/api/

``` 

 Accéder au conteneur en ligne de commande

```bash
docker exec -it exam-web-1 bash
``` 
Redémarrer avec une base propre (si besoin)
```bash
docker compose down -v
docker compose up --build
```
>[!CAUTION]
>⚠️ Le flag -v supprime aussi le volume (donc la base de données SQLite).

## 📂 Structure du projet

```bash
exam
├── db.sqlite3  # Base de données locale
├── docker-compose.yml # Orchestration Docker
├── Dockerfile  # Image backend
├── exam          # Configuration Django
│   ├── asgi.py
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   ├── settings.cpython-312.pyc
│   │   ├── urls.cpython-312.pyc
│   │   └── wsgi.cpython-312.pyc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── project_manager # App principale (Users & Projects)
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations  # Fichiers migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── README.md
└── requirements.txt    # Dépendances Python

```
 ## 🔐 Authentification JWT
 
 - Obtenir un token : POST /api/users/login/

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```
- Rafraîchir le token : POST /api/users/token/refresh/
```json
{
  "refresh": "<refresh_token>"
}
```
>[!NOTE]
>L'authentification est requise (Bearer Token) pour accéder aux routes protégées.

## 🧪 Endpoints disponibles

| Méthode | Route                 | Description                      |
| ------: | --------------------- | -------------------------------- |
|    POST | `/api/users/register/`| Créer un compte utilisateur      |
|    POST | `/api/users/login/`   | Se connecter (JWT)               |
|     GET | `/api/projects/`      | Lister les projets               |
|    POST | `/api/projects/`      | Créer un projet (auth requis)    |
|     GET | `/api/projects/<id>/` | Détail d’un projet               |
|     PUT | `/api/projects/<id>/` | Modifier un projet (si owner)    |
|  DELETE | `/api/projects/<id>/` | Supprimer un projet (si owner)   |


## 🧰 Dépendances principales

- Django
- Django REST Framework
- SimpleJWT
- django-filter

## 🛠️ Développement local

1. Lancer le backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
2. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

## ✅ Tests

Ce projet inclut une suite de tests automatisés basée sur `APITestCase` de Django REST Framework. Elle couvre :

- ✅ L'enregistrement d'utilisateurs (`/users/register/`)
- ✅ L'authentification JWT (`/users/login/`)
- ✅ La création, la mise à jour et la suppression de projets (avec vérification des permissions)

 ```bash
 python manage.py test

```
>[!NOTE]
>Django crée une base de données temporaire (test_db) pendant l’exécution.

    ✅ Résultat attendu

 ```bash
 ........
----------------------------------------------------------------------
Ran 8 tests in 7.1s
OK

```

📁 Emplacement des tests

Tous les tests sont dans le fichier suivant :

```bash
project_manager/tests.py
```
🔍 Ce que testent les scénarios

| Classe         | Méthode                               | Comportement vérifié             |
| -------------- | ------------------------------------- | -------------------------------- |
| `UserTests`    | `test_user_registration`              | Création d’un compte utilisateur |
| `AuthTests`    | `test_login_jwt`                      | Connexion avec token JWT         |
| `ProjectTests` | `test_create_project_authenticated`   | Création de projet (connecté)    |
|                | `test_create_project_unauthenticated` | Création rejetée (non connecté)  |
|                | `test_update_project_by_owner`        | Mise à jour par le propriétaire  |
|                | `test_update_project_by_other_user`   | Mise à jour refusée (403)        |
|                | `test_delete_project_by_owner`        | Suppression par le propriétaire  |
|                | `test_delete_project_by_other_user`   | Suppression refusée (403)        |

> [!TIP]
> 🛠 Astuce développement
> Pour lancer un seul test :

```bash
python manage.py test project_manager.tests.ProjectTests.test_create_project_authenticated
```

## 🚀 CI/CD (tests automatisés)

Ce projet utilise **GitHub Actions** pour exécuter automatiquement les tests à chaque :

- `push` sur la branche `main`
- création/modification de `pull request` vers `main`

### 🔍 Objectif

Assurer que tout le projet reste fonctionnel à chaque mise à jour, sans casser de fonctionnalité.

### ⚙️ Workflow déclenché

Le workflow (`.github/workflows/tests.yml`) :

- Installe les dépendances Python
- Applique les migrations
- Exécute la suite de tests avec la commande


## 📌 Notes

- La base de données par défaut est SQLite.
- Le projet utilise une permission personnalisée IsOwnerOrReadOnly.
- La pagination est configurée via CustomPagination.
