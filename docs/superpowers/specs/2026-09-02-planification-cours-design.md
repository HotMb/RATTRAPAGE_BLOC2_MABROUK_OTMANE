# Application de planification des cours — Design

Date : 2026-09-02
Contexte : projet de rattrapage Bloc 2 (Efficom) — application web de gestion et
consultation de planning de cours, avec rôles admin/intervenant/étudiant et
détection de conflits de réservation.

## 1. Objectif et exigences métier

- Un administrateur gère les données (classes, salles, intervenants, étudiants,
  cours) et voit tout le planning.
- Un intervenant et un étudiant ont un accès **lecture seule** à leur propre
  planning (respectivement : cours qu'il donne / cours de sa classe).
- Une salle, une classe ou un intervenant ne peut pas être mobilisé sur deux
  séances qui se chevauchent. Deux cours consécutifs (fin = début) sont
  autorisés.
- Toutes les autorisations sont contrôlées côté back-end (Django), jamais
  seulement par le masquage d'éléments d'UI.

## 2. Stack et architecture globale

```
RATTRAPAGE_BLOC2_MABROUK_OTMANE/
├── backend/          Django + Django REST Framework + MySQL
├── frontend/         React (Create React App)
└── README.md         Racine : install, lancement, tests, comptes démo
```

- **Auth** : JWT via `djangorestframework-simplejwt`. Le login renvoie un
  `access` + `refresh` token ; React les stocke (mémoire + `localStorage`) et
  les envoie via l'en-tête `Authorization: Bearer <token>`.
- **Autorisations** : permission classes DRF côté serveur ; React ne fait que
  refléter l'état pour l'ergonomie (pas une mesure de sécurité).
- **Échanges** : API REST/JSON pure sous `/api/`.
- **Base de données** : MySQL installé nativement en local, accès via
  `django.db.backends.mysql`, paramètres lus depuis un fichier `.env` non
  commité (voir §7).

## 3. Modèle de données (Django, app unique `planning`)

Une seule app Django `planning` : le domaine est petit et fortement couplé,
pas besoin de le découper.

- **User** (hérite de `AbstractUser`)
  - champs hérités : `username`, `password` (hachage géré par Django)
  - `role` : `CharField` choix `ADMIN` / `INTERVENANT` / `ETUDIANT`

- **Classe** : `nom`, `niveau`

- **Salle** : `nom_ou_numero`, `capacite`, `type`

- **Intervenant**
  - `user` : `OneToOneField(User)`
  - `nom`, `prenom`, `email`

- **Etudiant**
  - `user` : `OneToOneField(User)`
  - `nom`, `prenom`, `email`
  - `classe` : `ForeignKey(Classe)`

- **Cours**
  - `intitule`
  - `classe` : `ForeignKey(Classe)`
  - `salle` : `ForeignKey(Salle)`
  - `intervenant` : `ForeignKey(Intervenant)`
  - `debut`, `fin` : `DateTimeField`

### Règles de validation (partagées serializer + modèle, non dupliquées)

- `fin` doit être strictement postérieur à `debut`.
- Détection de conflit : un `Cours` C2 entre en conflit avec un `Cours` C1
  existant si (même salle OU même classe OU même intervenant) ET
  `C2.debut < C1.fin` ET `C2.fin > C1.debut`.
- Lors d'une modification, le cours en cours d'édition est exclu de la
  comparaison (`exclude(pk=self.pk)`).
- Deux cours consécutifs (`10:00-11:00` après `09:00-10:00`) sont acceptés
  (l'inégalité est stricte).
- Le formulaire admin "Nouvel intervenant" / "Nouvel étudiant" crée en une
  transaction le `User` (avec rôle) et la fiche métier liée.

## 4. API & permissions

Endpoints DRF (ViewSets + routeur), tous sous `/api/` :

| Endpoint | Accès |
|---|---|
| `POST /api/auth/login/` | Public — retourne tokens JWT + rôle |
| `POST /api/auth/refresh/` | Public (avec refresh token valide) |
| `/api/classes/`, `/api/salles/` | Admin : CRUD complet. Autres rôles : lecture seule |
| `/api/intervenants/`, `/api/etudiants/` | Admin : CRUD complet. Autres rôles : aucun accès |
| `/api/cours/` | Admin : CRUD complet (+ 409 si conflit). Intervenant : lecture seule filtrée sur ses cours. Étudiant : lecture seule filtrée sur les cours de sa classe |

Points de sécurité :
- Le filtrage par rôle est fait dans `get_queryset()`, à partir de
  `request.user` (dérivé du token JWT) — jamais à partir d'un paramètre
  fourni par le client. Un étudiant ne peut donc pas voir les cours d'une
  autre classe en modifiant l'URL/les query params.
- Permission custom refusant tout `POST/PUT/PATCH/DELETE` non-admin avec
  `403 Forbidden`.
- Un conflit de planning renvoie `409 Conflict` avec un message précisant la
  ressource en cause (salle, classe ou intervenant, et le cours concerné).
- Filtres de consultation sur `/api/cours/` : `date`, et pour l'admin
  également `classe`, `salle`, `intervenant` (query params).

## 5. Frontend React (Create React App)

```
frontend/src/
├── api/            client HTTP (fetch wrapper, attache le token JWT)
├── auth/           AuthContext (user, role, login, logout)
├── components/     éléments réutilisables (formulaires, liste, message d'erreur)
├── pages/
│   ├── LoginPage
│   ├── PlanningPage        (liste des cours + filtres, adaptée au rôle)
│   ├── ClassesPage         (admin)
│   ├── SallesPage          (admin)
│   ├── IntervenantsPage    (admin)
│   ├── EtudiantsPage       (admin)
│   └── CoursFormPage       (création/édition, admin)
└── App.jsx          routing (react-router-dom) + routes protégées par rôle
```

- State management : Context API + state local par page avec `fetch` (pas de
  Redux, application trop petite pour le justifier).
- `RequireRole` protège les routes et masque les actions non permises — pur
  confort UX, la sécurité réelle reste côté Django.
- Les erreurs `400` (validation) et `409` (conflit) de l'API sont affichées
  clairement dans le formulaire concerné.
- Accessibilité/responsive : `<label htmlFor>` sur tous les champs, layout
  flexbox/grid + media queries pour mobile, navigation utilisable au clavier.

## 6. Tests

**Django** (`backend/planning/tests/`), via `APITestCase` (DRF), couvrant au
minimum :
1. Création valide d'un cours
2. Refus si `fin <= debut`
3. Détection conflit de salle
4. Détection conflit d'intervenant
5. Acceptation de deux cours consécutifs
6. Refus d'écriture (403) pour intervenant/étudiant
7. Limitation du planning selon le profil connecté

Compléments : conflit de classe, exclusion du cours lui-même en modification,
relation obligatoire manquante.

**React** (Jest + React Testing Library, inclus avec CRA), tests ciblés :
- Formulaire de login (saisie, soumission, affichage d'erreur)
- Affichage conditionnel des menus/actions selon le rôle
- Affichage d'un message de conflit 409 dans le formulaire de cours

Commandes documentées dans le README : `python manage.py test` et
`CI=true npm test`.

## 7. Configuration, secrets et README

- `backend/.env` (ignoré par git) + `.env.example` (valeurs factices commitées)
  pour `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Commande de management `python manage.py seed_demo` créant les 3 comptes de
  démonstration (admin / intervenant / étudiant) + quelques classes, salles et
  cours d'exemple.
- Le README documente, dans l'ordre : prérequis, création de la base MySQL,
  installation backend, migrations + seed, lancement backend, installation +
  lancement frontend, exécution des tests, et les 3 comptes de démo avec leurs
  identifiants/mots de passe factices.

## Hors périmètre (YAGNI, à ne pas construire)

- Auto-inscription des utilisateurs (tous les comptes sont créés par l'admin).
- Réinitialisation de mot de passe / e-mail.
- Vue calendaire (amélioration facultative non retenue pour cette version).
- Redux ou toute librairie de state management additionnelle.
