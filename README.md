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
docker-compose down -v
docker-compose up --build
```
>[!CAUTION]
>⚠️ Le flag -v supprime aussi le volume (donc la base de données SQLite).

## 📂 Structure du projet

```bash
exam/
├── project_manager/     # App principale (Users & Projects)
├── exam/                # Configuration Django
├── db.sqlite3           # Base de données locale
├── Dockerfile           # Image backend
├── docker-compose.yml   # Orchestration Docker
├── requirements.txt     # Dépendances Python
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
|     GET | `/api/projects/`      | Lister les projets (auth requis) |
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
2. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## ✅ Tests

 ```bash
 python manage.py test
```

## 📌 Notes

La base de données par défaut est SQLite.
Le projet utilise une permission personnalisée IsOwnerOrReadOnly.
La pagination est configurée via CustomPagination.
