# Application de planification des cours

Application web de gestion et de consultation du planning de cours pour Efficom :
un administrateur gère les données et les séances, les intervenants et étudiants
consultent en lecture seule leur propre planning. Le back-end refuse toute
séance qui chevaucherait une salle, une classe ou un intervenant déjà occupé
sur le créneau (statut HTTP 409).

## Stack technique

- **Front-end** : React (Create React App), react-router-dom
- **Back-end** : Python / Django + Django REST Framework, authentification JWT
- **Base de données** : MySQL (via l'ORM Django)
- **Tests** : `django.test` / DRF `APITestCase` côté back-end, Jest + React Testing Library côté front-end

## Prérequis

- Python 3.11+ (testé avec 3.13)
- Node.js 18+ et npm
- MySQL Server 8.x installé et démarré localement

## 1. Créer la base MySQL

Se connecter à MySQL en administrateur (ex : `mysql -u root -p`) et exécuter :

```sql
CREATE DATABASE planification_cours CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'planification_user'@'localhost' IDENTIFIED BY 'change-me-locally';
GRANT ALL PRIVILEGES ON planification_cours.* TO 'planification_user'@'localhost';
GRANT ALL PRIVILEGES ON test_planification_cours.* TO 'planification_user'@'localhost';
FLUSH PRIVILEGES;
```

La deuxième base (`test_planification_cours`) est créée et détruite automatiquement
par Django à chaque exécution des tests : les droits doivent être accordés à l'avance.

## 2. Installer et lancer le back-end (Django)

```bash
cd backend
python -m venv venv
```

Activer l'environnement virtuel :
- Windows (PowerShell) : `venv\Scripts\Activate.ps1`
- macOS/Linux : `source venv/bin/activate`

Puis :

```bash
pip install -r requirements.txt
cp .env.example .env   # Windows : Copy-Item .env.example .env
```

Éditer `backend/.env` avec vos identifiants MySQL réels (au minimum `SECRET_KEY`,
`DB_USER`, `DB_PASSWORD` s'ils diffèrent des valeurs par défaut ci-dessus).

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Le back-end est disponible sur `http://localhost:8000/`, l'API sur
`http://localhost:8000/api/`, l'admin Django sur `http://localhost:8000/admin/`.

## 3. Installer et lancer le front-end (React)

Dans un second terminal, à la racine du projet :

```bash
cd frontend
npm install
npm start
```

L'application est disponible sur `http://localhost:3000/`.

## 4. Exécuter les tests

**Back-end** (depuis `backend/`, avec le venv activé) :

```bash
python manage.py test
```

Couvre notamment : création valide d'un cours, refus d'une heure de fin
antérieure/égale au début, détection de conflit de salle, détection de
conflit d'intervenant, acceptation de deux cours consécutifs, refus
d'écriture (403) pour intervenant/étudiant, limitation du planning selon
le profil connecté.

**Front-end** (depuis `frontend/`) :

```bash
CI=true npm test -- --watchAll=false
```

## 5. Comptes de démonstration

Créés automatiquement par `python manage.py seed_demo` :

| Rôle           | Identifiant    | Mot de passe |
|----------------|----------------|--------------|
| Administrateur | `admin`        | `Demo1234!`  |
| Intervenant    | `intervenant1` | `Demo1234!`  |
| Étudiant       | `etudiant1`    | `Demo1234!`  |

## Rôles et permissions

| Profil         | Droits |
|----------------|--------|
| Administrateur | Accès complet (création, lecture, modification, suppression) aux classes, salles, intervenants, étudiants et cours. |
| Intervenant    | Lecture seule des cours qui lui sont affectés. |
| Étudiant       | Lecture seule des cours de sa classe. |

Toutes ces règles sont appliquées côté back-end (Django REST Framework, via des
classes de permission et un filtrage du queryset basé sur l'utilisateur du
token JWT) — l'interface React ne fait que refléter le rôle pour l'ergonomie,
ce n'est pas la mesure de sécurité.

## Sécurité et secrets

- `backend/.env` (non versionné, dans `.gitignore`) contient les vrais
  identifiants MySQL et la clé secrète Django.
- `backend/.env.example` documente les variables attendues avec des valeurs
  factices.
- L'application Django se connecte à MySQL avec un utilisateur dédié
  (`planification_user`), jamais avec le compte `root`.

## Structure du dépôt

```
backend/    Projet Django (API REST + admin)
frontend/   Application React (SPA)
```
