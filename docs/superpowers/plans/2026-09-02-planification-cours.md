# Application de planification des cours — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full working Django + React + MySQL course-scheduling application with role-based auth (admin/intervenant/étudiant), admin CRUD screens, read-only role-filtered planning views, and conflict-free scheduling enforced server-side.

**Architecture:** Django REST Framework backend (single app `planning`) exposing a JWT-authenticated JSON API under `/api/`, backed by MySQL. A Create React App frontend consumes that API exclusively — no server-rendered templates. Conflict detection and role-based data filtering happen only in Django; React reflects role state for UX only.

**Tech Stack:** Python/Django, Django REST Framework, djangorestframework-simplejwt, PyMySQL (pure-Python MySQL driver, avoids native build tooling on Windows), django-cors-headers, python-decouple, MySQL Server (native local install); React (Create React App), react-router-dom, Jest + React Testing Library (bundled with CRA).

**Spec:** `docs/superpowers/specs/2026-09-02-planification-cours-design.md`

## Global Constraints

- Auth is JWT (djangorestframework-simplejwt), not Django session cookies.
- Frontend is Create React App (not Vite) — an intentional choice, not a deprecation oversight.
- MySQL is installed natively on the machine (not Docker).
- Planning view is a sorted list with filters — no calendar UI in this plan.
- A single Django app named `planning` holds all models — do not split into per-entity apps.
- Admin creates an Intervenant/Étudiant via ONE combined form/request that creates the `User` and the linked profile together — never a two-step "create user, then link" flow.
- No Redux or other state library — Context API + local component state only.
- Two periods conflict when `new.debut < existing.fin AND new.fin > existing.debut`; consecutive courses (fin == debut) are allowed.
- All authorization decisions happen server-side; React-side role checks are UX only and must never be the only enforcement.
- Secrets (`SECRET_KEY`, DB credentials) live in `backend/.env` (gitignored); `backend/.env.example` ships with fake placeholder values.
- Commit locally after each task (see task steps) — do not `git push` or add a remote until the user confirms the whole app is finished.

---

## Task 1: Backend project scaffold and MySQL database

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/.gitignore`
- Create: `backend/manage.py` (via `django-admin startproject`)
- Create: `backend/config/settings.py`, `backend/config/urls.py`, `backend/config/wsgi.py`, `backend/config/asgi.py`, `backend/config/__init__.py`
- Create: `.gitignore` (repo root, for `frontend/node_modules`, etc. — created in Task 12)

**Interfaces:**
- Produces: a runnable (but app-less) Django project reachable at `http://localhost:8000/`, configured to read DB credentials from `backend/.env`, ready for `planning` app to be added in Task 2.

- [ ] **Step 1: Create the MySQL database and user**

Open a terminal with access to your local MySQL server (e.g. `mysql -u root -p`) and run:

```sql
CREATE DATABASE planification_cours CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'planification_user'@'localhost' IDENTIFIED BY 'change-me-locally';
GRANT ALL PRIVILEGES ON planification_cours.* TO 'planification_user'@'localhost';
GRANT ALL PRIVILEGES ON test_planification_cours.* TO 'planification_user'@'localhost';
FLUSH PRIVILEGES;
```

Note: MySQL grants are per-database-name, not inherited by prefix — the second `GRANT` is required (not just `ALL PRIVILEGES` on the real database) because Django's test runner creates and drops a separate `test_planification_cours` database when running `python manage.py test`.

- [ ] **Step 2: Create the Python virtual environment and install dependencies**

From the repo root:

```bash
cd backend
python -m venv venv
```

On Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```
On macOS/Linux:
```bash
source venv/bin/activate
```

Create `backend/requirements.txt`:

```
Django>=4.2,<5
djangorestframework>=3.14,<4
djangorestframework-simplejwt>=5.3,<6
PyMySQL>=1.1,<2
django-cors-headers>=4.3,<5
python-decouple>=3.8,<4
```

Install:
```bash
pip install -r requirements.txt
```

- [ ] **Step 3: Start the Django project**

```bash
django-admin startproject config .
```

(Run from inside `backend/`, the trailing `.` puts `manage.py` directly in `backend/` instead of a nested folder.)

- [ ] **Step 4: Configure PyMySQL as the MySQL driver**

Edit `backend/config/__init__.py`:

```python
import pymysql

pymysql.install_as_MySQLdb()
```

This makes Django's `django.db.backends.mysql` engine use the pure-Python PyMySQL driver instead of the `mysqlclient` C extension, which avoids needing a C compiler / MySQL dev headers on Windows.

- [ ] **Step 5: Create `.env.example` and `.env`**

Create `backend/.env.example` (committed, fake values):

```
SECRET_KEY=replace-with-a-random-secret-key
DEBUG=True
DB_NAME=planification_cours
DB_USER=planification_user
DB_PASSWORD=change-me-locally
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGIN=http://localhost:3000
```

Copy it to a real, gitignored `backend/.env` with your actual local values:

```bash
cp .env.example .env
```

(On Windows PowerShell: `Copy-Item .env.example .env`)

- [ ] **Step 6: Create `backend/.gitignore`**

```
venv/
__pycache__/
*.pyc
.env
db.sqlite3
```

- [ ] **Step 7: Configure `backend/config/settings.py` for env vars, MySQL, DRF, JWT, CORS**

Replace the relevant parts of the generated `backend/config/settings.py`:

```python
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'planning',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

AUTH_USER_MODEL = 'planning.User'

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CORS_ALLOWED_ORIGINS = [
    config('CORS_ALLOWED_ORIGIN', default='http://localhost:3000'),
]
```

Also keep Django's default `TEMPLATES`, `AUTH_PASSWORD_VALIDATORS` blocks from the generated file as-is.

Note: `AUTH_USER_MODEL = 'planning.User'` references a model that does not exist yet — this is intentional and fixed in Task 2, which must run its migration before any other app's migration.

- [ ] **Step 8: Verify the project boots (expected to fail right now — that's fine)**

```bash
python manage.py check
```

Expected: an error mentioning it cannot find `planning` app / `planning.User` — confirms settings are wired correctly and we're ready for Task 2. Do not attempt `migrate` yet.

- [ ] **Step 9: Commit**

```bash
git add backend/requirements.txt backend/.env.example backend/.gitignore backend/manage.py backend/config
git commit -m "chore: scaffold Django project with MySQL, DRF, JWT, CORS config"
```

---

## Task 2: Custom User model with roles

**Files:**
- Create: `backend/planning/__init__.py`, `backend/planning/apps.py` (via `startapp`)
- Create: `backend/planning/models.py`
- Create: `backend/planning/admin.py`
- Create: `backend/planning/tests/__init__.py`
- Create: `backend/planning/tests/test_user_model.py`

**Interfaces:**
- Produces: `User` model (app `planning`) with `role` field and `Role` choices (`ADMIN`, `INTERVENANT`, `ETUDIANT`), importable as `from planning.models import User`. All later tasks depend on `User.Role`.

- [ ] **Step 1: Create the `planning` app**

```bash
python manage.py startapp planning
```

- [ ] **Step 2: Create `backend/planning/tests/` package and remove the generated `tests.py`**

```bash
rm backend/planning/tests.py
mkdir backend/planning/tests
touch backend/planning/tests/__init__.py
```

(On Windows PowerShell: `Remove-Item backend\planning\tests.py; New-Item -ItemType Directory backend\planning\tests; New-Item -ItemType File backend\planning\tests\__init__.py`)

- [ ] **Step 3: Write the failing test for the User model and role choices**

Create `backend/planning/tests/test_user_model.py`:

```python
from django.test import TestCase
from planning.models import User


class UserRoleTests(TestCase):
    def test_user_has_role_field_with_expected_choices(self):
        user = User.objects.create_user(
            username='alice', password='pass1234', role=User.Role.ADMIN
        )
        self.assertEqual(user.role, 'ADMIN')
        self.assertIn(('ADMIN', 'Administrateur'), User.Role.choices)
        self.assertIn(('INTERVENANT', 'Intervenant'), User.Role.choices)
        self.assertIn(('ETUDIANT', 'Étudiant'), User.Role.choices)
```

- [ ] **Step 4: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_user_model
```

Expected: FAIL (import error or `AUTH_USER_MODEL` app not migrated yet — the goal here is to confirm the model doesn't exist).

- [ ] **Step 5: Implement the `User` model**

Create `backend/planning/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        INTERVENANT = 'INTERVENANT', 'Intervenant'
        ETUDIANT = 'ETUDIANT', 'Étudiant'

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f'{self.username} ({self.role})'
```

- [ ] **Step 6: Register `User` in the admin**

Create `backend/planning/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    list_display = ('username', 'role', 'is_staff', 'is_active')


admin.site.register(User, UserAdmin)
```

- [ ] **Step 7: Create and run the first migration**

```bash
python manage.py makemigrations planning
python manage.py migrate
```

Expected: succeeds, creates all default Django tables plus `planning_user`.

- [ ] **Step 8: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_user_model
```

Expected: PASS (1 test).

- [ ] **Step 9: Commit**

```bash
git add backend/planning
git commit -m "feat: add custom User model with role field"
```

---

## Task 3: Classe and Salle models

**Files:**
- Modify: `backend/planning/models.py`
- Modify: `backend/planning/admin.py`
- Create: `backend/planning/tests/test_classe_salle_models.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Classe` (`nom`, `niveau`) and `Salle` (`nom_ou_numero`, `capacite`, `type`) models, importable from `planning.models`. Used by `Etudiant` and `Cours` in later tasks.

- [ ] **Step 1: Write the failing test**

Create `backend/planning/tests/test_classe_salle_models.py`:

```python
from django.test import TestCase
from planning.models import Classe, Salle


class ClasseSalleModelTests(TestCase):
    def test_create_classe(self):
        classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.assertEqual(str(classe), 'BTS SIO 1')

    def test_create_salle(self):
        salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.assertEqual(salle.capacite, 30)
        self.assertEqual(str(salle), 'A101')
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_classe_salle_models
```

Expected: FAIL with `ImportError: cannot import name 'Classe'`.

- [ ] **Step 3: Implement the models**

Append to `backend/planning/models.py`:

```python
class Classe(models.Model):
    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class Salle(models.Model):
    nom_ou_numero = models.CharField(max_length=50)
    capacite = models.PositiveIntegerField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.nom_ou_numero
```

- [ ] **Step 4: Register in admin**

Append to `backend/planning/admin.py`:

```python
from .models import Classe, Salle

admin.site.register(Classe)
admin.site.register(Salle)
```

- [ ] **Step 5: Migrate**

```bash
python manage.py makemigrations planning
python manage.py migrate
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_classe_salle_models
```

Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add backend/planning
git commit -m "feat: add Classe and Salle models"
```

---

## Task 4: Intervenant and Etudiant models

**Files:**
- Modify: `backend/planning/models.py`
- Modify: `backend/planning/admin.py`
- Create: `backend/planning/tests/test_intervenant_etudiant_models.py`

**Interfaces:**
- Consumes: `User`, `Classe` from Tasks 2-3.
- Produces: `Intervenant` (`user` OneToOne, `nom`, `prenom`, `email`) and `Etudiant` (`user` OneToOne, `nom`, `prenom`, `email`, `classe` FK). Default reverse accessors `user.intervenant` and `user.etudiant` are relied on by the `Cours` queryset filtering in Task 9.

- [ ] **Step 1: Write the failing test**

Create `backend/planning/tests/test_intervenant_etudiant_models.py`:

```python
from django.test import TestCase
from planning.models import User, Classe, Intervenant, Etudiant


class IntervenantEtudiantModelTests(TestCase):
    def test_create_intervenant_linked_to_user(self):
        user = User.objects.create_user(username='jdupont', password='pass1234', role=User.Role.INTERVENANT)
        intervenant = Intervenant.objects.create(user=user, nom='Dupont', prenom='Jean', email='j.dupont@efficom.fr')
        self.assertEqual(user.intervenant, intervenant)

    def test_create_etudiant_linked_to_user_and_classe(self):
        classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        user = User.objects.create_user(username='amartin', password='pass1234', role=User.Role.ETUDIANT)
        etudiant = Etudiant.objects.create(user=user, nom='Martin', prenom='Alice', email='a.martin@efficom.fr', classe=classe)
        self.assertEqual(user.etudiant, etudiant)
        self.assertEqual(etudiant.classe, classe)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_intervenant_etudiant_models
```

Expected: FAIL with `ImportError: cannot import name 'Intervenant'`.

- [ ] **Step 3: Implement the models**

Append to `backend/planning/models.py`:

```python
class Intervenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='intervenant')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f'{self.prenom} {self.nom}'


class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etudiant')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='etudiants')

    def __str__(self):
        return f'{self.prenom} {self.nom}'
```

- [ ] **Step 4: Register in admin**

Append to `backend/planning/admin.py`:

```python
from .models import Intervenant, Etudiant

admin.site.register(Intervenant)
admin.site.register(Etudiant)
```

- [ ] **Step 5: Migrate**

```bash
python manage.py makemigrations planning
python manage.py migrate
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_intervenant_etudiant_models
```

Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add backend/planning
git commit -m "feat: add Intervenant and Etudiant models"
```

---

## Task 5: Cours model and conflict-detection function

**Files:**
- Modify: `backend/planning/models.py`
- Modify: `backend/planning/admin.py`
- Create: `backend/planning/tests/test_cours_conflicts.py`

**Interfaces:**
- Consumes: `Classe`, `Salle`, `Intervenant` from Tasks 3-4.
- Produces: `Cours` model (`intitule`, `classe`, `salle`, `intervenant`, `debut`, `fin`) and module-level function `find_conflicting_cours(*, salle, classe, intervenant, debut, fin, exclude_pk=None) -> tuple[str, Cours] | None` in `planning/models.py`. Consumed directly by the serializer in Task 9.

- [ ] **Step 1: Write the failing tests for the conflict-detection function**

Create `backend/planning/tests/test_cours_conflicts.py`:

```python
from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime

from planning.models import User, Classe, Salle, Intervenant, Cours, find_conflicting_cours


def dt(y, m, d, h, mi=0):
    return make_aware(datetime(y, m, d, h, mi))


class ConflictDetectionTests(TestCase):
    def setUp(self):
        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.classe2 = Classe.objects.create(nom='BTS SIO 2', niveau='BTS2')
        self.salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.salle2 = Salle.objects.create(nom_ou_numero='A102', capacite=30, type='TD')

        user1 = User.objects.create_user(username='interv1', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant = Intervenant.objects.create(user=user1, nom='Dupont', prenom='Jean', email='j@efficom.fr')
        user2 = User.objects.create_user(username='interv2', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant2 = Intervenant.objects.create(user=user2, nom='Martin', prenom='Alice', email='a@efficom.fr')

        self.existing = Cours.objects.create(
            intitule='Maths', classe=self.classe, salle=self.salle, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9), fin=dt(2026, 9, 10, 10),
        )

    def test_no_conflict_for_unrelated_slot(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 14), fin=dt(2026, 9, 10, 15),
        )
        self.assertIsNone(result)

    def test_consecutive_slot_is_not_a_conflict(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 10), fin=dt(2026, 9, 10, 11),
        )
        self.assertIsNone(result)

    def test_salle_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe2, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, 'la salle')
        self.assertEqual(cours, self.existing)

    def test_intervenant_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe2, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, "l'intervenant")
        self.assertEqual(cours, self.existing)

    def test_classe_conflict_detected(self):
        result = find_conflicting_cours(
            salle=self.salle2, classe=self.classe, intervenant=self.intervenant2,
            debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30),
        )
        self.assertIsNotNone(result)
        ressource, cours = result
        self.assertEqual(ressource, 'la classe')

    def test_excludes_self_when_editing(self):
        result = find_conflicting_cours(
            salle=self.salle, classe=self.classe, intervenant=self.intervenant,
            debut=dt(2026, 9, 10, 9), fin=dt(2026, 9, 10, 10),
            exclude_pk=self.existing.pk,
        )
        self.assertIsNone(result)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test planning.tests.test_cours_conflicts
```

Expected: FAIL with `ImportError: cannot import name 'Cours'`.

- [ ] **Step 3: Implement the `Cours` model and `find_conflicting_cours`**

Append to `backend/planning/models.py`:

```python
class Cours(models.Model):
    intitule = models.CharField(max_length=200)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name='cours')
    salle = models.ForeignKey(Salle, on_delete=models.PROTECT, related_name='cours')
    intervenant = models.ForeignKey(Intervenant, on_delete=models.PROTECT, related_name='cours')
    debut = models.DateTimeField()
    fin = models.DateTimeField()

    class Meta:
        ordering = ['debut']

    def __str__(self):
        return f'{self.intitule} ({self.debut:%d/%m/%Y %H:%M})'


def find_conflicting_cours(*, salle, classe, intervenant, debut, fin, exclude_pk=None):
    """Return (ressource_label, Cours) for the first overlapping course, or None."""
    overlapping = Cours.objects.filter(debut__lt=fin, fin__gt=debut)
    if exclude_pk is not None:
        overlapping = overlapping.exclude(pk=exclude_pk)

    salle_conflict = overlapping.filter(salle=salle).first()
    if salle_conflict:
        return ('la salle', salle_conflict)

    classe_conflict = overlapping.filter(classe=classe).first()
    if classe_conflict:
        return ('la classe', classe_conflict)

    intervenant_conflict = overlapping.filter(intervenant=intervenant).first()
    if intervenant_conflict:
        return ("l'intervenant", intervenant_conflict)

    return None
```

- [ ] **Step 4: Register in admin**

Append to `backend/planning/admin.py`:

```python
from .models import Cours

admin.site.register(Cours)
```

- [ ] **Step 5: Migrate**

```bash
python manage.py makemigrations planning
python manage.py migrate
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python manage.py test planning.tests.test_cours_conflicts
```

Expected: PASS (6 tests).

- [ ] **Step 7: Commit**

```bash
git add backend/planning
git commit -m "feat: add Cours model with server-side conflict detection"
```

---

## Task 6: JWT authentication endpoints

**Files:**
- Create: `backend/planning/serializers.py`
- Create: `backend/planning/views.py`
- Create: `backend/planning/urls.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`
- Create: `backend/planning/tests/test_auth.py`

**Interfaces:**
- Consumes: `User.Role` from Task 2.
- Produces: `POST /api/auth/login/` returning `{access, refresh, username, role}`; `POST /api/auth/refresh/` returning a new `access` token. Used by the React `AuthContext` in Task 13.

- [ ] **Step 1: Write the failing test**

Create `backend/planning/tests/test_auth.py`:

```python
from rest_framework.test import APITestCase
from rest_framework import status
from planning.models import User


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)

    def test_login_returns_tokens_and_role(self):
        response = self.client.post('/api/auth/login/', {'username': 'admin1', 'password': 'pass1234'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], 'ADMIN')
        self.assertEqual(response.data['username'], 'admin1')

    def test_login_with_wrong_password_rejected(self):
        response = self.client.post('/api/auth/login/', {'username': 'admin1', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_auth
```

Expected: FAIL with 404 (no `/api/auth/login/` route yet).

- [ ] **Step 3: Add simplejwt settings**

Append to `backend/config/settings.py`:

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

- [ ] **Step 4: Create the login serializer/view**

Create `backend/planning/serializers.py`:

```python
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        return data
```

Create `backend/planning/views.py`:

```python
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RoleTokenObtainPairSerializer


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer
```

- [ ] **Step 5: Wire up URLs**

Create `backend/planning/urls.py`:

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RoleTokenObtainPairView

urlpatterns = [
    path('auth/login/', RoleTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
]
```

Edit `backend/config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('planning.urls')),
]
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_auth
```

Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add backend/planning backend/config
git commit -m "feat: add JWT login/refresh endpoints with role in response"
```

---

## Task 7: Permissions module, Classe and Salle API

**Files:**
- Create: `backend/planning/permissions.py`
- Modify: `backend/planning/serializers.py`
- Modify: `backend/planning/views.py`
- Modify: `backend/planning/urls.py`
- Create: `backend/planning/tests/test_classe_salle_api.py`

**Interfaces:**
- Consumes: `User.Role` (Task 2), `Classe`/`Salle` (Task 3).
- Produces: `IsAdminOrReadOnly` permission class (reused by Tasks 8-9); `/api/classes/` and `/api/salles/` CRUD endpoints (admin write, everyone-authenticated read).

- [ ] **Step 1: Write the failing test**

Create `backend/planning/tests/test_classe_salle_api.py`:

```python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from planning.models import User, Classe


class ClasseApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)
        self.etudiant_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=self.etudiant_user)

    def test_admin_can_create_classe(self):
        response = self.admin_client.post('/api/classes/', {'nom': 'BTS SIO 1', 'niveau': 'BTS1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_etudiant_can_read_but_not_create_classe(self):
        Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        list_response = self.etudiant_client.get('/api/classes/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        create_response = self.etudiant_client.post('/api/classes/', {'nom': 'X', 'niveau': 'Y'}, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_read_classes(self):
        anonymous_client = APIClient()
        response = anonymous_client.get('/api/classes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_classe_salle_api
```

Expected: FAIL with 404 (no `/api/classes/` route yet).

- [ ] **Step 3: Implement the shared permission class**

Create `backend/planning/permissions.py`:

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdminOrReadOnly(BasePermission):
    """Authenticated users may read; only ADMIN may write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == User.Role.ADMIN


class IsAdmin(BasePermission):
    """Only ADMIN may access at all."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )
```

- [ ] **Step 4: Add serializers**

Append to `backend/planning/serializers.py`:

```python
from rest_framework import serializers

from .models import Classe, Salle


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau']


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['id', 'nom_ou_numero', 'capacite', 'type']
```

- [ ] **Step 5: Add viewsets**

Append to `backend/planning/views.py`:

```python
from rest_framework import viewsets

from .models import Classe, Salle
from .permissions import IsAdminOrReadOnly
from .serializers import ClasseSerializer, SalleSerializer


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all().order_by('nom')
    serializer_class = ClasseSerializer
    permission_classes = [IsAdminOrReadOnly]


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all().order_by('nom_ou_numero')
    serializer_class = SalleSerializer
    permission_classes = [IsAdminOrReadOnly]
```

- [ ] **Step 6: Wire up the router**

Replace `backend/planning/urls.py` with:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RoleTokenObtainPairView, ClasseViewSet, SalleViewSet

router = DefaultRouter()
router.register('classes', ClasseViewSet, basename='classe')
router.register('salles', SalleViewSet, basename='salle')

urlpatterns = [
    path('auth/login/', RoleTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('', include(router.urls)),
]
```

- [ ] **Step 7: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_classe_salle_api
```

Expected: PASS (3 tests).

- [ ] **Step 8: Commit**

```bash
git add backend/planning
git commit -m "feat: add Classe/Salle API with admin-write/read-only permissions"
```

---

## Task 8: Intervenant and Etudiant API (combined user+profile creation)

**Files:**
- Modify: `backend/planning/serializers.py`
- Modify: `backend/planning/views.py`
- Modify: `backend/planning/urls.py`
- Create: `backend/planning/tests/test_intervenant_etudiant_api.py`

**Interfaces:**
- Consumes: `IsAdmin` permission (Task 7), `Intervenant`/`Etudiant`/`Classe` models.
- Produces: `/api/intervenants/` and `/api/etudiants/` — admin-only CRUD; POST accepts `username`+`password` alongside profile fields and creates both the `User` and the profile row atomically.

- [ ] **Step 1: Write the failing test**

Create `backend/planning/tests/test_intervenant_etudiant_api.py`:

```python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from planning.models import User, Classe, Etudiant


class IntervenantEtudiantApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        self.etudiant_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=self.etudiant_user)

        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')

    def test_admin_creates_intervenant_with_linked_user_in_one_call(self):
        payload = {
            'nom': 'Dupont', 'prenom': 'Jean', 'email': 'j.dupont@efficom.fr',
            'username': 'jdupont', 'password': 'motdepasse123',
        }
        response = self.admin_client.post('/api/intervenants/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username='jdupont')
        self.assertEqual(created_user.role, User.Role.INTERVENANT)
        self.assertTrue(created_user.check_password('motdepasse123'))

    def test_admin_creates_etudiant_with_classe_and_linked_user(self):
        payload = {
            'nom': 'Martin', 'prenom': 'Alice', 'email': 'a.martin@efficom.fr',
            'classe': self.classe.id, 'username': 'amartin', 'password': 'motdepasse123',
        }
        response = self.admin_client.post('/api/etudiants/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        etudiant = Etudiant.objects.get(user__username='amartin')
        self.assertEqual(etudiant.classe, self.classe)

    def test_etudiant_cannot_access_intervenants_endpoint(self):
        response = self.etudiant_client.get('/api/intervenants/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python manage.py test planning.tests.test_intervenant_etudiant_api
```

Expected: FAIL with 404.

- [ ] **Step 3: Add serializers with combined create()**

Append to `backend/planning/serializers.py`:

```python
from .models import User, Intervenant, Etudiant


class IntervenantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Intervenant
        fields = ['id', 'nom', 'prenom', 'email', 'username', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Cet identifiant est déjà utilisé.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password, role=User.Role.INTERVENANT)
        return Intervenant.objects.create(user=user, **validated_data)


class EtudiantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Etudiant
        fields = ['id', 'nom', 'prenom', 'email', 'classe', 'username', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Cet identifiant est déjà utilisé.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password, role=User.Role.ETUDIANT)
        return Etudiant.objects.create(user=user, **validated_data)
```

- [ ] **Step 4: Add viewsets**

Append to `backend/planning/views.py`:

```python
from .models import Intervenant, Etudiant
from .permissions import IsAdmin
from .serializers import IntervenantSerializer, EtudiantSerializer


class IntervenantViewSet(viewsets.ModelViewSet):
    queryset = Intervenant.objects.select_related('user').all().order_by('nom')
    serializer_class = IntervenantSerializer
    permission_classes = [IsAdmin]


class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.select_related('user', 'classe').all().order_by('nom')
    serializer_class = EtudiantSerializer
    permission_classes = [IsAdmin]
```

- [ ] **Step 5: Register routes**

In `backend/planning/urls.py`, update the import and router registration:

```python
from .views import (
    RoleTokenObtainPairView, ClasseViewSet, SalleViewSet,
    IntervenantViewSet, EtudiantViewSet,
)

router = DefaultRouter()
router.register('classes', ClasseViewSet, basename='classe')
router.register('salles', SalleViewSet, basename='salle')
router.register('intervenants', IntervenantViewSet, basename='intervenant')
router.register('etudiants', EtudiantViewSet, basename='etudiant')
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python manage.py test planning.tests.test_intervenant_etudiant_api
```

Expected: PASS (3 tests).

- [ ] **Step 7: Commit**

```bash
git add backend/planning
git commit -m "feat: add admin-only Intervenant/Etudiant API with combined user creation"
```

---

## Task 9: Cours API — conflict detection (409), role filtering, validation

This is the task that covers most of the mandatory test scenarios from the spec.

**Files:**
- Modify: `backend/planning/serializers.py`
- Modify: `backend/planning/views.py`
- Modify: `backend/planning/urls.py`
- Create: `backend/planning/tests/test_cours_api.py`

**Interfaces:**
- Consumes: `find_conflicting_cours` (Task 5), `IsAdminOrReadOnly` (Task 7), `User.Role`.
- Produces: `/api/cours/` — admin CRUD with `409 Conflict` on scheduling clashes and `400` on `fin <= debut`; intervenant/étudiant get a role-filtered read-only queryset; query params `date`, and (admin only) `classe`, `salle`, `intervenant` filter the list.

- [ ] **Step 1: Write the failing tests**

Create `backend/planning/tests/test_cours_api.py`:

```python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils.timezone import make_aware
from datetime import datetime

from planning.models import User, Classe, Salle, Intervenant, Etudiant, Cours


def dt(y, m, d, h, mi=0):
    return make_aware(datetime(y, m, d, h, mi)).isoformat()


class CoursApiTests(APITestCase):
    def setUp(self):
        self.classe = Classe.objects.create(nom='BTS SIO 1', niveau='BTS1')
        self.classe2 = Classe.objects.create(nom='BTS SIO 2', niveau='BTS2')
        self.salle = Salle.objects.create(nom_ou_numero='A101', capacite=30, type='TD')
        self.salle2 = Salle.objects.create(nom_ou_numero='A102', capacite=30, type='TD')

        self.admin = User.objects.create_user(username='admin1', password='pass1234', role=User.Role.ADMIN)

        interv_user = User.objects.create_user(username='interv1', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant = Intervenant.objects.create(user=interv_user, nom='Dupont', prenom='Jean', email='j@efficom.fr')
        interv_user2 = User.objects.create_user(username='interv2', password='pass1234', role=User.Role.INTERVENANT)
        self.intervenant2 = Intervenant.objects.create(user=interv_user2, nom='Martin', prenom='Alice', email='a@efficom.fr')

        etu_user = User.objects.create_user(username='etu1', password='pass1234', role=User.Role.ETUDIANT)
        self.etudiant = Etudiant.objects.create(user=etu_user, nom='Petit', prenom='Sam', email='s@efficom.fr', classe=self.classe)

        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)
        self.intervenant_client = APIClient()
        self.intervenant_client.force_authenticate(user=interv_user)
        self.etudiant_client = APIClient()
        self.etudiant_client.force_authenticate(user=etu_user)

        self.existing = Cours.objects.create(
            intitule='Maths', classe=self.classe, salle=self.salle, intervenant=self.intervenant,
            debut=make_aware(datetime(2026, 9, 10, 9)), fin=make_aware(datetime(2026, 9, 10, 10)),
        )

    def _payload(self, **overrides):
        payload = {
            'intitule': 'Anglais', 'classe': self.classe2.id, 'salle': self.salle2.id,
            'intervenant': self.intervenant2.id,
            'debut': dt(2026, 9, 10, 14), 'fin': dt(2026, 9, 10, 15),
        }
        payload.update(overrides)
        return payload

    def test_create_valid_cours(self):
        response = self.admin_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fin_before_or_equal_debut_rejected(self):
        response = self.admin_client.post(
            '/api/cours/', self._payload(fin=dt(2026, 9, 10, 14)), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_salle_conflict_returns_409(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(salle=self.salle.id, debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_intervenant_conflict_returns_409(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(intervenant=self.intervenant.id, debut=dt(2026, 9, 10, 9, 30), fin=dt(2026, 9, 10, 10, 30)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_consecutive_cours_accepted(self):
        response = self.admin_client.post(
            '/api/cours/',
            self._payload(salle=self.salle.id, classe=self.classe.id, intervenant=self.intervenant.id,
                           debut=dt(2026, 9, 10, 10), fin=dt(2026, 9, 10, 11)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_updating_cours_excludes_itself_from_conflict_check(self):
        response = self.admin_client.patch(
            f'/api/cours/{self.existing.id}/', {'intitule': 'Maths avancées'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_write_forbidden_for_intervenant_and_etudiant(self):
        response = self.intervenant_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.etudiant_client.post('/api/cours/', self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_intervenant_sees_only_own_cours(self):
        Cours.objects.create(
            intitule='Anglais', classe=self.classe2, salle=self.salle2, intervenant=self.intervenant2,
            debut=make_aware(datetime(2026, 9, 10, 14)), fin=make_aware(datetime(2026, 9, 10, 15)),
        )
        response = self.intervenant_client.get('/api/cours/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.existing.id)

    def test_etudiant_sees_only_own_classe_cours(self):
        Cours.objects.create(
            intitule='Anglais', classe=self.classe2, salle=self.salle2, intervenant=self.intervenant2,
            debut=make_aware(datetime(2026, 9, 10, 14)), fin=make_aware(datetime(2026, 9, 10, 15)),
        )
        response = self.etudiant_client.get('/api/cours/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.existing.id)

    def test_admin_can_filter_by_classe_salle_intervenant_and_date(self):
        response = self.admin_client.get(f'/api/cours/?classe={self.classe.id}')
        self.assertEqual(len(response.data), 1)

        response = self.admin_client.get('/api/cours/?date=2026-09-10')
        self.assertEqual(len(response.data), 1)

        response = self.admin_client.get('/api/cours/?date=2026-09-11')
        self.assertEqual(len(response.data), 0)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test planning.tests.test_cours_api
```

Expected: FAIL with 404 (no `/api/cours/` route yet).

- [ ] **Step 3: Add the `ConflictError` exception and `CoursSerializer`**

Append to `backend/planning/serializers.py`:

```python
from rest_framework.exceptions import APIException

from .models import Cours, find_conflicting_cours


# DRF's default exception handler reads status_code off APIException subclasses directly.
class ConflictError(APIException):
    status_code = 409
    default_code = 'conflict'


class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = ['id', 'intitule', 'classe', 'salle', 'intervenant', 'debut', 'fin']

    def validate(self, attrs):
        debut = attrs.get('debut', getattr(self.instance, 'debut', None))
        fin = attrs.get('fin', getattr(self.instance, 'fin', None))
        salle = attrs.get('salle', getattr(self.instance, 'salle', None))
        classe = attrs.get('classe', getattr(self.instance, 'classe', None))
        intervenant = attrs.get('intervenant', getattr(self.instance, 'intervenant', None))

        if debut is not None and fin is not None and fin <= debut:
            raise serializers.ValidationError(
                {'fin': "L'heure de fin doit être postérieure à l'heure de début."}
            )

        if salle and classe and intervenant and debut and fin:
            exclude_pk = self.instance.pk if self.instance else None
            conflict = find_conflicting_cours(
                salle=salle, classe=classe, intervenant=intervenant,
                debut=debut, fin=fin, exclude_pk=exclude_pk,
            )
            if conflict:
                ressource, cours_conflit = conflict
                raise ConflictError(
                    f"Conflit détecté : {ressource} est déjà occupé(e) par le cours "
                    f"« {cours_conflit.intitule} » du "
                    f"{cours_conflit.debut:%d/%m/%Y %H:%M} au {cours_conflit.fin:%d/%m/%Y %H:%M}."
                )

        return attrs
```

- [ ] **Step 4: Add the `CoursViewSet` with role-based queryset and permission**

Append to `backend/planning/views.py`:

```python
from datetime import datetime, timedelta

from django.utils.timezone import make_aware

from .models import Cours
from .serializers import CoursSerializer


class CoursViewSet(viewsets.ModelViewSet):
    serializer_class = CoursSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Cours.objects.select_related('classe', 'salle', 'intervenant').order_by('debut')

        if user.role == User.Role.INTERVENANT:
            qs = qs.filter(intervenant__user=user)
        elif user.role == User.Role.ETUDIANT:
            etudiant = getattr(user, 'etudiant', None)
            qs = qs.filter(classe=etudiant.classe) if etudiant else qs.none()

        date_str = self.request.query_params.get('date')
        if date_str:
            day_start = make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
            qs = qs.filter(debut__gte=day_start, debut__lt=day_start + timedelta(days=1))

        if user.role == User.Role.ADMIN:
            for param, field in (('classe', 'classe_id'), ('salle', 'salle_id'), ('intervenant', 'intervenant_id')):
                value = self.request.query_params.get(param)
                if value:
                    qs = qs.filter(**{field: value})

        return qs
```

Note: `User` must be imported in `views.py` (`from .models import User, ...`).

Note: the date filter deliberately avoids Django's `debut__date=date_str` lookup. On MySQL with `USE_TZ=True`, that lookup requires the server-side `CONVERT_TZ` function, which needs the `mysql.time_zone_name` tables populated (via `mysql_tzinfo_to_sql`, which isn't available out of the box on Windows) — without them `CONVERT_TZ` silently returns `NULL` and the filter matches nothing. Filtering with an explicit `debut__gte`/`debut__lt` range computed in Python sidesteps that requirement entirely and works on any MySQL install.

- [ ] **Step 5: Register the route**

In `backend/planning/urls.py`:

```python
from .views import (
    RoleTokenObtainPairView, ClasseViewSet, SalleViewSet,
    IntervenantViewSet, EtudiantViewSet, CoursViewSet,
)

router.register('cours', CoursViewSet, basename='cours')
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python manage.py test planning.tests.test_cours_api
```

Expected: PASS (10 tests).

- [ ] **Step 7: Run the full backend test suite**

```bash
python manage.py test
```

Expected: all tests across all files PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/planning
git commit -m "feat: add Cours API with conflict detection (409) and role-filtered planning"
```

---

## Task 10: Demo data seed command

**Files:**
- Create: `backend/planning/management/__init__.py`
- Create: `backend/planning/management/commands/__init__.py`
- Create: `backend/planning/management/commands/seed_demo.py`

**Interfaces:**
- Produces: `python manage.py seed_demo` — idempotent command creating 3 demo accounts (`admin`/`intervenant1`/`etudiant1`) plus sample classes, salles, and a couple of non-conflicting cours. Documented in the README (Task 19).

- [ ] **Step 1: Create the management command package**

```bash
mkdir -p backend/planning/management/commands
touch backend/planning/management/__init__.py
touch backend/planning/management/commands/__init__.py
```

(PowerShell: `New-Item -ItemType Directory -Force backend\planning\management\commands; New-Item -ItemType File backend\planning\management\__init__.py; New-Item -ItemType File backend\planning\management\commands\__init__.py`)

- [ ] **Step 2: Write the command**

Create `backend/planning/management/commands/seed_demo.py`:

```python
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from planning.models import User, Classe, Salle, Intervenant, Etudiant, Cours

DEMO_PASSWORD = 'Demo1234!'


class Command(BaseCommand):
    help = 'Seed demo accounts and sample scheduling data.'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='admin', defaults={'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password(DEMO_PASSWORD)
            admin.save()

        classe, _ = Classe.objects.get_or_create(nom='BTS SIO 1', defaults={'niveau': 'BTS1'})
        salle, _ = Salle.objects.get_or_create(nom_ou_numero='A101', defaults={'capacite': 30, 'type': 'TD'})

        interv_user, created = User.objects.get_or_create(
            username='intervenant1', defaults={'role': User.Role.INTERVENANT},
        )
        if created:
            interv_user.set_password(DEMO_PASSWORD)
            interv_user.save()
        intervenant, _ = Intervenant.objects.get_or_create(
            user=interv_user, defaults={'nom': 'Dupont', 'prenom': 'Jean', 'email': 'j.dupont@efficom.fr'},
        )

        etu_user, created = User.objects.get_or_create(
            username='etudiant1', defaults={'role': User.Role.ETUDIANT},
        )
        if created:
            etu_user.set_password(DEMO_PASSWORD)
            etu_user.save()
        Etudiant.objects.get_or_create(
            user=etu_user, defaults={'nom': 'Martin', 'prenom': 'Alice', 'email': 'a.martin@efficom.fr', 'classe': classe},
        )

        Cours.objects.get_or_create(
            intitule='Mathématiques', classe=classe, salle=salle, intervenant=intervenant,
            debut=make_aware(datetime(2026, 9, 15, 9)), fin=make_aware(datetime(2026, 9, 15, 10)),
        )
        Cours.objects.get_or_create(
            intitule='Anglais', classe=classe, salle=salle, intervenant=intervenant,
            debut=make_aware(datetime(2026, 9, 15, 10)), fin=make_aware(datetime(2026, 9, 15, 11)),
        )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready. Accounts: admin/{DEMO_PASSWORD}, intervenant1/{DEMO_PASSWORD}, etudiant1/{DEMO_PASSWORD}'
        ))
```

- [ ] **Step 3: Run it manually and verify**

```bash
python manage.py seed_demo
```

Expected: prints the success message; running it a second time does not error or duplicate rows (thanks to `get_or_create`).

- [ ] **Step 4: Commit**

```bash
git add backend/planning/management
git commit -m "feat: add seed_demo management command for demo accounts"
```

---

## Task 11: React app scaffold and API client

**Files:**
- Create: `frontend/` (via `npx create-react-app`)
- Create: `frontend/.env`
- Create: `frontend/src/api/client.js`
- Create: `.gitignore` at repo root

**Interfaces:**
- Produces: `apiRequest(path, {method, body})` and `extractErrorMessage(data)` in `frontend/src/api/client.js`, plus `setTokens`/`getTokens` helpers. Consumed by `AuthContext` (Task 12) and every page from Task 14 onward.

- [ ] **Step 1: Scaffold the React app**

From the repo root:

```bash
npx create-react-app frontend
```

- [ ] **Step 2: Point the frontend at the backend API**

Create `frontend/.env`:

```
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

- [ ] **Step 3: Create the root `.gitignore`**

Create `.gitignore` at the repo root (CRA's own `frontend/.gitignore` already covers `node_modules`, but this keeps the root clean too):

```
backend/venv/
backend/.env
backend/__pycache__/
**/__pycache__/
frontend/node_modules/
```

- [ ] **Step 4: Write the API client**

Create `frontend/src/api/client.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

function getTokens() {
  const raw = localStorage.getItem('auth_tokens');
  return raw ? JSON.parse(raw) : null;
}

export function setTokens(tokens) {
  if (tokens) {
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  } else {
    localStorage.removeItem('auth_tokens');
  }
}

export async function apiRequest(path, { method = 'GET', body } = {}) {
  const tokens = getTokens();
  const headers = { 'Content-Type': 'application/json' };
  if (tokens && tokens.access) {
    headers['Authorization'] = `Bearer ${tokens.access}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw { status: response.status, data };
  }

  return data;
}

export function extractErrorMessage(data) {
  if (!data) return 'Une erreur est survenue.';
  if (data.detail) return data.detail;
  return Object.entries(data)
    .map(([field, messages]) => `${field} : ${Array.isArray(messages) ? messages.join(' ') : messages}`)
    .join(' ');
}
```

- [ ] **Step 5: Verify the app boots**

```bash
cd frontend
npm start
```

Expected: default CRA page opens at `http://localhost:3000`. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 6: Commit**

```bash
git add frontend .gitignore
git commit -m "chore: scaffold React app with API client"
```

---

## Task 12: AuthContext and LoginPage

**Files:**
- Create: `frontend/src/auth/AuthContext.jsx`
- Create: `frontend/src/pages/LoginPage.jsx`
- Create: `frontend/src/pages/LoginPage.test.jsx`
- Modify: `frontend/src/App.js` → rename to `frontend/src/App.jsx` (or keep `.js`, matching CRA default — see Step 4)

**Interfaces:**
- Consumes: `apiRequest`, `setTokens` from Task 11.
- Produces: `AuthProvider`, `useAuth()` returning `{ user: {username, role} | null, login(username, password), logout() }`. Consumed by `RequireRole` (Task 13) and every page.

- [ ] **Step 1: Install react-router-dom**

```bash
cd frontend
npm install react-router-dom
```

- [ ] **Step 2: Write the AuthContext**

Create `frontend/src/auth/AuthContext.jsx`:

```jsx
import { createContext, useContext, useState, useCallback } from 'react';
import { apiRequest, setTokens } from '../api/client';

const AuthContext = createContext(null);

function readStoredUser() {
  const raw = localStorage.getItem('auth_user');
  return raw ? JSON.parse(raw) : null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser());

  const login = useCallback(async (username, password) => {
    const data = await apiRequest('/auth/login/', { method: 'POST', body: { username, password } });
    setTokens({ access: data.access, refresh: data.refresh });
    const nextUser = { username: data.username, role: data.role };
    localStorage.setItem('auth_user', JSON.stringify(nextUser));
    setUser(nextUser);
    return nextUser;
  }, []);

  const logout = useCallback(() => {
    setTokens(null);
    localStorage.removeItem('auth_user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
```

- [ ] **Step 3: Write the failing test for LoginPage**

Create `frontend/src/pages/LoginPage.test.jsx`:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { AuthProvider } from '../auth/AuthContext';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
  setTokens: jest.fn(),
}));

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

test('submits credentials and shows an error on invalid login', async () => {
  apiClient.apiRequest.mockRejectedValueOnce({ status: 401, data: { detail: 'No active account found' } });
  renderLoginPage();

  fireEvent.change(screen.getByLabelText(/identifiant/i), { target: { value: 'baduser' } });
  fireEvent.change(screen.getByLabelText(/mot de passe/i), { target: { value: 'badpass' } });
  fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));

  await waitFor(() => {
    expect(screen.getByRole('alert')).toHaveTextContent(/identifiant ou mot de passe incorrect/i);
  });
});

test('calls apiRequest with the entered credentials', async () => {
  apiClient.apiRequest.mockResolvedValueOnce({ access: 'a', refresh: 'b', username: 'admin', role: 'ADMIN' });
  renderLoginPage();

  fireEvent.change(screen.getByLabelText(/identifiant/i), { target: { value: 'admin' } });
  fireEvent.change(screen.getByLabelText(/mot de passe/i), { target: { value: 'pass1234' } });
  fireEvent.click(screen.getByRole('button', { name: /se connecter/i }));

  await waitFor(() => {
    expect(apiClient.apiRequest).toHaveBeenCalledWith('/auth/login/', {
      method: 'POST',
      body: { username: 'admin', password: 'pass1234' },
    });
  });
});
```

- [ ] **Step 4: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false LoginPage
```

Expected: FAIL (`Cannot find module './LoginPage'`).

- [ ] **Step 5: Implement LoginPage**

Create `frontend/src/pages/LoginPage.jsx`:

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/planning');
    } catch (err) {
      setError('Identifiant ou mot de passe incorrect.');
    }
  }

  return (
    <main>
      <form onSubmit={handleSubmit} aria-label="Formulaire de connexion">
        <h1>Connexion</h1>
        <div>
          <label htmlFor="username">Identifiant</label>
          <input
            id="username" name="username" value={username}
            onChange={(e) => setUsername(e.target.value)} required
          />
        </div>
        <div>
          <label htmlFor="password">Mot de passe</label>
          <input
            id="password" name="password" type="password" value={password}
            onChange={(e) => setPassword(e.target.value)} required
          />
        </div>
        {error && <p role="alert">{error}</p>}
        <button type="submit">Se connecter</button>
      </form>
    </main>
  );
}
```

- [ ] **Step 6: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false LoginPage
```

Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add frontend/src
git commit -m "feat: add AuthContext and LoginPage"
```

---

## Task 13: Routing, RequireRole, and NavBar

**Files:**
- Create: `frontend/src/components/RequireRole.jsx`
- Create: `frontend/src/components/NavBar.jsx`
- Modify: `frontend/src/App.js`
- Create: `frontend/src/App.test.js` (replace CRA's default)
- Create placeholder pages: `frontend/src/pages/PlanningPage.jsx`, `ClassesPage.jsx`, `SallesPage.jsx`, `IntervenantsPage.jsx`, `EtudiantsPage.jsx`, `CoursFormPage.jsx` (fleshed out in Tasks 14-17; here they're minimal so routing compiles and is testable)

**Interfaces:**
- Consumes: `useAuth()` from Task 12.
- Produces: `<RequireRole roles={[...]}>` wrapper component; app routes `/login`, `/planning`, `/classes`, `/salles`, `/intervenants`, `/etudiants`, `/cours/nouveau`, `/cours/:id/modifier`.

- [ ] **Step 1: Write the failing test for role-based navigation**

Create `frontend/src/App.test.js` (overwrite the CRA default):

```jsx
import { render, screen } from '@testing-library/react';
import App from './App';

function setStoredUser(user) {
  localStorage.setItem('auth_user', JSON.stringify(user));
  localStorage.setItem('auth_tokens', JSON.stringify({ access: 'fake', refresh: 'fake' }));
}

afterEach(() => localStorage.clear());

test('etudiant does not see admin management links', () => {
  setStoredUser({ username: 'etu1', role: 'ETUDIANT' });
  render(<App />);
  expect(screen.queryByRole('link', { name: /classes/i })).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: /planning/i })).toBeInTheDocument();
});

test('admin sees admin management links', () => {
  setStoredUser({ username: 'admin', role: 'ADMIN' });
  render(<App />);
  expect(screen.getByRole('link', { name: /classes/i })).toBeInTheDocument();
});
```

`App` renders its own `AuthProvider` internally (see Step 6 below), so the test renders `<App />` directly without wrapping it in another provider.

- [ ] **Step 2: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false App.test
```

Expected: FAIL (App still renders the default CRA page, no nav links).

- [ ] **Step 3: Create minimal placeholder pages**

Create each of the following with the same minimal shape (example for `frontend/src/pages/ClassesPage.jsx`, repeat for `SallesPage.jsx`, `IntervenantsPage.jsx`, `EtudiantsPage.jsx`, `CoursFormPage.jsx` substituting the heading text):

```jsx
export default function ClassesPage() {
  return <h1>Classes</h1>;
}
```

Create `frontend/src/pages/PlanningPage.jsx`:

```jsx
export default function PlanningPage() {
  return <h1>Planning</h1>;
}
```

(These are placeholders; Tasks 14-17 replace their bodies with real functionality without changing the export shape, so routing in this task never has to change.)

- [ ] **Step 4: Implement `RequireRole`**

Create `frontend/src/components/RequireRole.jsx`:

```jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function RequireRole({ roles, children }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/planning" replace />;
  }
  return children;
}
```

- [ ] **Step 5: Implement `NavBar`**

Create `frontend/src/components/NavBar.jsx`:

```jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function NavBar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <nav aria-label="Navigation principale">
      <Link to="/planning">Planning</Link>
      {user.role === 'ADMIN' && (
        <>
          <Link to="/classes">Classes</Link>
          <Link to="/salles">Salles</Link>
          <Link to="/intervenants">Intervenants</Link>
          <Link to="/etudiants">Étudiants</Link>
        </>
      )}
      <span>{user.username} ({user.role})</span>
      <button type="button" onClick={logout}>Déconnexion</button>
    </nav>
  );
}
```

- [ ] **Step 6: Wire up `App.js`**

Replace `frontend/src/App.js`:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import RequireRole from './components/RequireRole';
import NavBar from './components/NavBar';
import LoginPage from './pages/LoginPage';
import PlanningPage from './pages/PlanningPage';
import ClassesPage from './pages/ClassesPage';
import SallesPage from './pages/SallesPage';
import IntervenantsPage from './pages/IntervenantsPage';
import EtudiantsPage from './pages/EtudiantsPage';
import CoursFormPage from './pages/CoursFormPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/planning" element={<RequireRole><PlanningPage /></RequireRole>} />
          <Route path="/classes" element={<RequireRole roles={['ADMIN']}><ClassesPage /></RequireRole>} />
          <Route path="/salles" element={<RequireRole roles={['ADMIN']}><SallesPage /></RequireRole>} />
          <Route path="/intervenants" element={<RequireRole roles={['ADMIN']}><IntervenantsPage /></RequireRole>} />
          <Route path="/etudiants" element={<RequireRole roles={['ADMIN']}><EtudiantsPage /></RequireRole>} />
          <Route path="/cours/nouveau" element={<RequireRole roles={['ADMIN']}><CoursFormPage /></RequireRole>} />
          <Route path="/cours/:id/modifier" element={<RequireRole roles={['ADMIN']}><CoursFormPage /></RequireRole>} />
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

- [ ] **Step 7: Delete the obsolete default CRA test assets**

Delete `frontend/src/App.css` references that no longer apply if any import errors surface, and delete `frontend/src/logo.svg` import from `App.js` (already removed by the rewrite above). No action needed if `App.js` was fully replaced as shown.

- [ ] **Step 8: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false App.test
```

Expected: PASS (2 tests).

- [ ] **Step 9: Commit**

```bash
git add frontend/src
git commit -m "feat: add routing, RequireRole guard, and role-aware NavBar"
```

---

## Task 14: PlanningPage — role-filtered list with filters

**Files:**
- Modify: `frontend/src/pages/PlanningPage.jsx`
- Create: `frontend/src/pages/PlanningPage.test.jsx`

**Interfaces:**
- Consumes: `apiRequest`, `useAuth()`.
- Produces: a fully working planning list screen; no new exports consumed elsewhere.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/pages/PlanningPage.test.jsx`:

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PlanningPage from './PlanningPage';
import { AuthProvider } from '../auth/AuthContext';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

beforeEach(() => {
  localStorage.setItem('auth_user', JSON.stringify({ username: 'etu1', role: 'ETUDIANT' }));
});
afterEach(() => localStorage.clear());

test('renders the fetched courses sorted by date/time', async () => {
  apiClient.apiRequest.mockResolvedValueOnce([
    {
      id: 1, intitule: 'Maths', debut: '2026-09-15T09:00:00Z', fin: '2026-09-15T10:00:00Z',
      classe: 1, salle: 1, intervenant: 1,
    },
  ]);

  render(
    <MemoryRouter>
      <AuthProvider>
        <PlanningPage />
      </AuthProvider>
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(screen.getByText('Maths')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false PlanningPage
```

Expected: FAIL (placeholder page has no course list).

- [ ] **Step 3: Implement `PlanningPage`**

Replace `frontend/src/pages/PlanningPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import { useAuth } from '../auth/AuthContext';

function buildQuery(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return query ? `?${query}` : '';
}

export default function PlanningPage() {
  const { user } = useAuth();
  const [cours, setCours] = useState([]);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ date: '', classe: '', salle: '', intervenant: '' });

  const loadCours = useCallback(async () => {
    setError('');
    try {
      const data = await apiRequest(`/cours/${buildQuery(filters)}`);
      setCours(data);
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }, [filters]);

  useEffect(() => {
    loadCours();
  }, [loadCours]);

  function handleFilterChange(field) {
    return (event) => setFilters((prev) => ({ ...prev, [field]: event.target.value }));
  }

  return (
    <main>
      <h1>Planning</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="filter-date">Date</label>
        <input id="filter-date" type="date" value={filters.date} onChange={handleFilterChange('date')} />

        {user.role === 'ADMIN' && (
          <>
            <label htmlFor="filter-classe">Classe (id)</label>
            <input id="filter-classe" value={filters.classe} onChange={handleFilterChange('classe')} />
            <label htmlFor="filter-salle">Salle (id)</label>
            <input id="filter-salle" value={filters.salle} onChange={handleFilterChange('salle')} />
            <label htmlFor="filter-intervenant">Intervenant (id)</label>
            <input id="filter-intervenant" value={filters.intervenant} onChange={handleFilterChange('intervenant')} />
          </>
        )}
      </form>

      {error && <p role="alert">{error}</p>}

      <table>
        <thead>
          <tr>
            <th scope="col">Intitulé</th>
            <th scope="col">Classe</th>
            <th scope="col">Salle</th>
            <th scope="col">Intervenant</th>
            <th scope="col">Début</th>
            <th scope="col">Fin</th>
          </tr>
        </thead>
        <tbody>
          {cours.map((c) => (
            <tr key={c.id}>
              <td>{c.intitule}</td>
              <td>{c.classe}</td>
              <td>{c.salle}</td>
              <td>{c.intervenant}</td>
              <td>{new Date(c.debut).toLocaleString('fr-FR')}</td>
              <td>{new Date(c.fin).toLocaleString('fr-FR')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

Note: the table shows raw FK ids for classe/salle/intervenant at this stage — acceptable per the spec ("intitulé, classe, salle, intervenant et horaires" minimum), and can be enriched later by having the API return nested representations, which is out of scope for this plan.

- [ ] **Step 4: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false PlanningPage
```

Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/PlanningPage.jsx frontend/src/pages/PlanningPage.test.jsx
git commit -m "feat: implement role-aware planning list with filters"
```

---

## Task 15: Admin CRUD — Classes and Salles pages

**Files:**
- Modify: `frontend/src/pages/ClassesPage.jsx`
- Modify: `frontend/src/pages/SallesPage.jsx`
- Create: `frontend/src/components/EntityTable.jsx`
- Create: `frontend/src/pages/ClassesPage.test.jsx`

**Interfaces:**
- Consumes: `apiRequest`, `extractErrorMessage`.
- Produces: `<EntityTable columns={[{key, label}]} rows={[...]} onEdit={fn} onDelete={fn} />` reusable component, consumed again in Task 16.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/pages/ClassesPage.test.jsx`:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ClassesPage from './ClassesPage';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

test('creates a classe and refreshes the list', async () => {
  apiClient.apiRequest
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce({ id: 1, nom: 'BTS SIO 1', niveau: 'BTS1' })
    .mockResolvedValueOnce([{ id: 1, nom: 'BTS SIO 1', niveau: 'BTS1' }]);

  render(<ClassesPage />);

  fireEvent.change(screen.getByLabelText(/nom/i), { target: { value: 'BTS SIO 1' } });
  fireEvent.change(screen.getByLabelText(/niveau/i), { target: { value: 'BTS1' } });
  fireEvent.click(screen.getByRole('button', { name: /ajouter/i }));

  await waitFor(() => {
    expect(screen.getByText('BTS SIO 1')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false ClassesPage
```

Expected: FAIL (placeholder page has no form).

- [ ] **Step 3: Implement the reusable `EntityTable`**

Create `frontend/src/components/EntityTable.jsx`:

```jsx
export default function EntityTable({ columns, rows, onDelete }) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key} scope="col">{col.label}</th>
          ))}
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            {columns.map((col) => (
              <td key={col.key}>{row[col.key]}</td>
            ))}
            <td>
              <button type="button" onClick={() => onDelete(row.id)}>Supprimer</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

- [ ] **Step 4: Implement `ClassesPage`**

Replace `frontend/src/pages/ClassesPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'niveau', label: 'Niveau' },
];

export default function ClassesPage() {
  const [classes, setClasses] = useState([]);
  const [nom, setNom] = useState('');
  const [niveau, setNiveau] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/classes/');
    setClasses(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/classes/', { method: 'POST', body: { nom, niveau } });
      setNom('');
      setNiveau('');
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/classes/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main>
      <h1>Classes</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={nom} onChange={(e) => setNom(e.target.value)} required />
        <label htmlFor="niveau">Niveau</label>
        <input id="niveau" value={niveau} onChange={(e) => setNiveau(e.target.value)} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <EntityTable columns={COLUMNS} rows={classes} onDelete={handleDelete} />
    </main>
  );
}
```

- [ ] **Step 5: Implement `SallesPage`** (same pattern, different fields)

Replace `frontend/src/pages/SallesPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom_ou_numero', label: 'Nom / numéro' },
  { key: 'capacite', label: 'Capacité' },
  { key: 'type', label: 'Type' },
];

export default function SallesPage() {
  const [salles, setSalles] = useState([]);
  const [nomOuNumero, setNomOuNumero] = useState('');
  const [capacite, setCapacite] = useState('');
  const [type, setType] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/salles/');
    setSalles(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/salles/', {
        method: 'POST',
        body: { nom_ou_numero: nomOuNumero, capacite: Number(capacite), type },
      });
      setNomOuNumero('');
      setCapacite('');
      setType('');
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/salles/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main>
      <h1>Salles</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="nom_ou_numero">Nom ou numéro</label>
        <input id="nom_ou_numero" value={nomOuNumero} onChange={(e) => setNomOuNumero(e.target.value)} required />
        <label htmlFor="capacite">Capacité</label>
        <input id="capacite" type="number" min="1" value={capacite} onChange={(e) => setCapacite(e.target.value)} required />
        <label htmlFor="type">Type</label>
        <input id="type" value={type} onChange={(e) => setType(e.target.value)} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <EntityTable columns={COLUMNS} rows={salles} onDelete={handleDelete} />
    </main>
  );
}
```

- [ ] **Step 6: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false ClassesPage
```

Expected: PASS (1 test).

- [ ] **Step 7: Commit**

```bash
git add frontend/src
git commit -m "feat: add admin CRUD screens for Classes and Salles"
```

---

## Task 16: Admin CRUD — Intervenants and Étudiants (combined form)

**Files:**
- Modify: `frontend/src/pages/IntervenantsPage.jsx`
- Modify: `frontend/src/pages/EtudiantsPage.jsx`
- Create: `frontend/src/pages/IntervenantsPage.test.jsx`

**Interfaces:**
- Consumes: `apiRequest`, `extractErrorMessage`, `EntityTable` (Task 15).
- Produces: nothing consumed elsewhere; terminal pages.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/pages/IntervenantsPage.test.jsx`:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import IntervenantsPage from './IntervenantsPage';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

test('creates an intervenant with a linked account in one submission', async () => {
  apiClient.apiRequest
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce({ id: 1, nom: 'Dupont', prenom: 'Jean', email: 'j@efficom.fr' })
    .mockResolvedValueOnce([{ id: 1, nom: 'Dupont', prenom: 'Jean', email: 'j@efficom.fr' }]);

  render(<IntervenantsPage />);

  fireEvent.change(screen.getByLabelText(/^nom$/i), { target: { value: 'Dupont' } });
  fireEvent.change(screen.getByLabelText(/prénom/i), { target: { value: 'Jean' } });
  fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'j@efficom.fr' } });
  fireEvent.change(screen.getByLabelText(/identifiant/i), { target: { value: 'jdupont' } });
  fireEvent.change(screen.getByLabelText(/mot de passe/i), { target: { value: 'motdepasse123' } });
  fireEvent.click(screen.getByRole('button', { name: /ajouter/i }));

  await waitFor(() => {
    expect(screen.getByText('Dupont')).toBeInTheDocument();
  });

  expect(apiClient.apiRequest).toHaveBeenNthCalledWith(2, '/intervenants/', {
    method: 'POST',
    body: { nom: 'Dupont', prenom: 'Jean', email: 'j@efficom.fr', username: 'jdupont', password: 'motdepasse123' },
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false IntervenantsPage
```

Expected: FAIL.

- [ ] **Step 3: Implement `IntervenantsPage`**

Replace `frontend/src/pages/IntervenantsPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'prenom', label: 'Prénom' },
  { key: 'email', label: 'Email' },
];

const EMPTY_FORM = { nom: '', prenom: '', email: '', username: '', password: '' };

export default function IntervenantsPage() {
  const [intervenants, setIntervenants] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/intervenants/');
    setIntervenants(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/intervenants/', { method: 'POST', body: form });
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/intervenants/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main>
      <h1>Intervenants</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={form.nom} onChange={handleChange('nom')} required />
        <label htmlFor="prenom">Prénom</label>
        <input id="prenom" value={form.prenom} onChange={handleChange('prenom')} required />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={handleChange('email')} required />
        <label htmlFor="username">Identifiant</label>
        <input id="username" value={form.username} onChange={handleChange('username')} required />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" value={form.password} onChange={handleChange('password')} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <EntityTable columns={COLUMNS} rows={intervenants} onDelete={handleDelete} />
    </main>
  );
}
```

- [ ] **Step 4: Implement `EtudiantsPage`** (same pattern, plus a `classe` select)

Replace `frontend/src/pages/EtudiantsPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'prenom', label: 'Prénom' },
  { key: 'email', label: 'Email' },
  { key: 'classe', label: 'Classe (id)' },
];

const EMPTY_FORM = { nom: '', prenom: '', email: '', classe: '', username: '', password: '' };

export default function EtudiantsPage() {
  const [etudiants, setEtudiants] = useState([]);
  const [classes, setClasses] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const [etudiantsData, classesData] = await Promise.all([
      apiRequest('/etudiants/'),
      apiRequest('/classes/'),
    ]);
    setEtudiants(etudiantsData);
    setClasses(classesData);
  }, []);

  useEffect(() => { load(); }, [load]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/etudiants/', { method: 'POST', body: { ...form, classe: Number(form.classe) } });
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/etudiants/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main>
      <h1>Étudiants</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={form.nom} onChange={handleChange('nom')} required />
        <label htmlFor="prenom">Prénom</label>
        <input id="prenom" value={form.prenom} onChange={handleChange('prenom')} required />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={handleChange('email')} required />
        <label htmlFor="classe">Classe</label>
        <select id="classe" value={form.classe} onChange={handleChange('classe')} required>
          <option value="">-- Choisir --</option>
          {classes.map((c) => (
            <option key={c.id} value={c.id}>{c.nom}</option>
          ))}
        </select>
        <label htmlFor="username">Identifiant</label>
        <input id="username" value={form.username} onChange={handleChange('username')} required />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" value={form.password} onChange={handleChange('password')} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <EntityTable columns={COLUMNS} rows={etudiants} onDelete={handleDelete} />
    </main>
  );
}
```

- [ ] **Step 5: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false IntervenantsPage
```

Expected: PASS (1 test).

- [ ] **Step 6: Commit**

```bash
git add frontend/src
git commit -m "feat: add admin CRUD screens for Intervenants and Etudiants"
```

---

## Task 17: CoursFormPage — create/edit with conflict and validation display

**Files:**
- Modify: `frontend/src/pages/CoursFormPage.jsx`
- Create: `frontend/src/pages/CoursFormPage.test.jsx`

**Interfaces:**
- Consumes: `apiRequest`, `extractErrorMessage`, `useNavigate`/`useParams` from react-router-dom.
- Produces: terminal page.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/pages/CoursFormPage.test.jsx`:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import CoursFormPage from './CoursFormPage';
import * as apiClient from '../api/client';

jest.mock('../api/client', () => ({
  ...jest.requireActual('../api/client'),
  apiRequest: jest.fn(),
}));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/cours/nouveau']}>
      <Routes>
        <Route path="/cours/nouveau" element={<CoursFormPage />} />
      </Routes>
    </MemoryRouter>
  );
}

test('shows the 409 conflict message returned by the API', async () => {
  apiClient.apiRequest
    .mockResolvedValueOnce([]) // classes
    .mockResolvedValueOnce([]) // salles
    .mockResolvedValueOnce([]) // intervenants
    .mockRejectedValueOnce({
      status: 409,
      data: { detail: 'Conflit détecté : la salle est déjà occupée par le cours « Maths ».' },
    });

  renderPage();

  fireEvent.change(screen.getByLabelText(/intitulé/i), { target: { value: 'Anglais' } });
  fireEvent.click(screen.getByRole('button', { name: /enregistrer/i }));

  await waitFor(() => {
    expect(screen.getByRole('alert')).toHaveTextContent(/conflit détecté/i);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
CI=true npm test -- --watchAll=false CoursFormPage
```

Expected: FAIL (placeholder page has no form).

- [ ] **Step 3: Implement `CoursFormPage`**

Replace `frontend/src/pages/CoursFormPage.jsx`:

```jsx
import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiRequest, extractErrorMessage } from '../api/client';

const EMPTY_FORM = { intitule: '', classe: '', salle: '', intervenant: '', debut: '', fin: '' };

export default function CoursFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [classes, setClasses] = useState([]);
  const [salles, setSalles] = useState([]);
  const [intervenants, setIntervenants] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const loadOptions = useCallback(async () => {
    const [classesData, sallesData, intervenantsData] = await Promise.all([
      apiRequest('/classes/'),
      apiRequest('/salles/'),
      apiRequest('/intervenants/'),
    ]);
    setClasses(classesData);
    setSalles(sallesData);
    setIntervenants(intervenantsData);
  }, []);

  useEffect(() => { loadOptions(); }, [loadOptions]);

  useEffect(() => {
    if (isEditing) {
      apiRequest(`/cours/${id}/`).then((data) => setForm({
        intitule: data.intitule,
        classe: data.classe,
        salle: data.salle,
        intervenant: data.intervenant,
        debut: data.debut.slice(0, 16),
        fin: data.fin.slice(0, 16),
      }));
    }
  }, [id, isEditing]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    const body = {
      intitule: form.intitule,
      classe: Number(form.classe),
      salle: Number(form.salle),
      intervenant: Number(form.intervenant),
      debut: form.debut,
      fin: form.fin,
    };
    try {
      if (isEditing) {
        await apiRequest(`/cours/${id}/`, { method: 'PATCH', body });
      } else {
        await apiRequest('/cours/', { method: 'POST', body });
      }
      navigate('/planning');
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  return (
    <main>
      <h1>{isEditing ? 'Modifier le cours' : 'Nouveau cours'}</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="intitule">Intitulé</label>
        <input id="intitule" value={form.intitule} onChange={handleChange('intitule')} required />

        <label htmlFor="classe">Classe</label>
        <select id="classe" value={form.classe} onChange={handleChange('classe')} required>
          <option value="">-- Choisir --</option>
          {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
        </select>

        <label htmlFor="salle">Salle</label>
        <select id="salle" value={form.salle} onChange={handleChange('salle')} required>
          <option value="">-- Choisir --</option>
          {salles.map((s) => <option key={s.id} value={s.id}>{s.nom_ou_numero}</option>)}
        </select>

        <label htmlFor="intervenant">Intervenant</label>
        <select id="intervenant" value={form.intervenant} onChange={handleChange('intervenant')} required>
          <option value="">-- Choisir --</option>
          {intervenants.map((i) => <option key={i.id} value={i.id}>{i.prenom} {i.nom}</option>)}
        </select>

        <label htmlFor="debut">Début</label>
        <input id="debut" type="datetime-local" value={form.debut} onChange={handleChange('debut')} required />

        <label htmlFor="fin">Fin</label>
        <input id="fin" type="datetime-local" value={form.fin} onChange={handleChange('fin')} required />

        {error && <p role="alert">{error}</p>}
        <button type="submit">Enregistrer</button>
      </form>
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
CI=true npm test -- --watchAll=false CoursFormPage
```

Expected: PASS (1 test).

- [ ] **Step 5: Add a "Nouveau cours" link to `PlanningPage` for admins**

In `frontend/src/pages/PlanningPage.jsx`, add near the top of the returned JSX (inside `<main>`, after `<h1>`):

```jsx
import { Link } from 'react-router-dom';
```

```jsx
{user.role === 'ADMIN' && <Link to="/cours/nouveau">Nouveau cours</Link>}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src
git commit -m "feat: add CoursFormPage with conflict/validation error display"
```

---

## Task 18: Basic responsive and accessible styling

**Files:**
- Modify: `frontend/src/App.css`
- Modify: `frontend/src/index.css`

**Interfaces:**
- Produces: no code interfaces — pure CSS affecting all pages already built.

- [ ] **Step 1: Replace `frontend/src/index.css`**

```css
:root {
  color-scheme: light;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #f5f5f7;
  color: #1a1a1a;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 3px solid #1a73e8;
  outline-offset: 2px;
}
```

- [ ] **Step 2: Replace `frontend/src/App.css`**

```css
main {
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem;
}

nav {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: #1a1a2e;
}

nav a,
nav span,
nav button {
  color: white;
}

nav button {
  background: transparent;
  border: 1px solid white;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  cursor: pointer;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 480px;
  margin-bottom: 1.5rem;
}

form label {
  font-weight: 600;
}

form input,
form select {
  padding: 0.5rem;
  font-size: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
}

[role="alert"] {
  color: #b00020;
  font-weight: 600;
}

@media (max-width: 600px) {
  table, thead, tbody, th, td, tr {
    display: block;
  }

  thead {
    display: none;
  }

  td {
    border: none;
    border-bottom: 1px solid #ccc;
  }
}
```

- [ ] **Step 3: Confirm `App.js` still imports `./App.css` and manually verify in the browser**

```bash
cd frontend
npm start
```

Open `http://localhost:3000`, resize the browser window to a mobile width, and confirm the nav wraps and the table becomes a stacked layout. Tab through the login form with the keyboard only and confirm a visible focus ring appears on each field and the submit button. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.css frontend/src/index.css
git commit -m "style: add responsive layout and visible keyboard focus states"
```

---

## Task 19: README

**Files:**
- Create: `README.md` (repo root)

**Interfaces:**
- Produces: none — documentation only.

- [ ] **Step 1: Write the README**

Create `README.md` at the repo root:

```markdown
# Application de planification des cours

Application web de gestion et de consultation du planning de cours pour Efficom :
un administrateur gère les données et les séances, les intervenants et étudiants
consultent en lecture seule leur propre planning. Le back-end refuse toute
séance qui chevaucherait une salle, une classe ou un intervenant déjà occupé
sur le créneau.

## Prérequis

- Python 3.11+
- Node.js 18+ et npm
- MySQL Server 8.x installé et démarré localement

## 1. Créer la base MySQL

Se connecter à MySQL (ex : `mysql -u root -p`) et exécuter :

```sql
CREATE DATABASE planification_cours CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'planification_user'@'localhost' IDENTIFIED BY 'change-me-locally';
GRANT ALL PRIVILEGES ON planification_cours.* TO 'planification_user'@'localhost';
FLUSH PRIVILEGES;
```

`ALL PRIVILEGES` (et non un accès en lecture/écriture seul) est nécessaire car
la suite de tests Django crée et supprime une base de test dédiée.

## 2. Installer et lancer le back-end (Django)

```bash
cd backend
python -m venv venv
# Windows : venv\Scripts\Activate.ps1
# macOS/Linux : source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis éditer .env avec vos identifiants MySQL réels
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Le back-end est disponible sur `http://localhost:8000/`, l'API sur
`http://localhost:8000/api/`.

## 3. Installer et lancer le front-end (React)

Dans un second terminal :

```bash
cd frontend
npm install
npm start
```

L'application est disponible sur `http://localhost:3000/`.

## 4. Exécuter les tests

Back-end (depuis `backend/`, avec le venv activé) :

```bash
python manage.py test
```

Front-end (depuis `frontend/`) :

```bash
CI=true npm test -- --watchAll=false
```

## 5. Comptes de démonstration

Créés par `python manage.py seed_demo` :

| Rôle         | Identifiant    | Mot de passe |
|--------------|----------------|--------------|
| Administrateur | `admin`        | `Demo1234!`  |
| Intervenant    | `intervenant1` | `Demo1234!`  |
| Étudiant       | `etudiant1`    | `Demo1234!`  |

## Rôles et permissions

| Profil         | Droits |
|----------------|--------|
| Administrateur | Accès complet (création, lecture, modification, suppression) aux classes, salles, intervenants, étudiants et cours. |
| Intervenant    | Lecture seule des cours qui lui sont affectés. |
| Étudiant       | Lecture seule des cours de sa classe. |

Toutes ces règles sont appliquées côté back-end (Django REST Framework) —
l'interface React ne fait que refléter le rôle pour l'ergonomie.

## Sécurité et secrets

Le fichier `backend/.env` (non versionné) contient les vrais identifiants
MySQL et la clé secrète Django. `backend/.env.example` documente les
variables attendues avec des valeurs factices.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add setup, testing, and demo account instructions"
```

---

## Final verification

- [ ] **Step 1: Run the full backend suite**

```bash
cd backend
python manage.py test
```

Expected: all tests pass (covers all 7 mandatory scenarios from the spec plus extras).

- [ ] **Step 2: Run the full frontend suite**

```bash
cd frontend
CI=true npm test -- --watchAll=false
```

Expected: all tests pass.

- [ ] **Step 3: Manual smoke test**

With both servers running (`python manage.py runserver` and `npm start`), log in as each of the 3 demo accounts in the browser and confirm:
- `admin` can create/edit/delete a classe, salle, intervenant, étudiant, and cours, and sees a `409` message when deliberately double-booking a salle.
- `intervenant1` sees only their own courses and has no management links.
- `etudiant1` sees only their class's courses and has no management links.
