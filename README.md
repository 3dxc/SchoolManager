# 🎓 SchoolManager — Système Intégré de Gestion Scolaire

**SchoolManager** est une solution web complète, moderne et responsive développée avec **Django**. Elle centralise la gestion administrative, pédagogique et financière des établissements d'enseignement du Mali — de la Maternelle au Doctorat.

---

## 📑 Table des matières

1. [Problématique & Objectifs](#-problématique--objectifs)
2. [Architecture Technique & Modèle Pivot](#-architecture-technique--modèle-pivot)
3. [Les 5 Applications Django](#-les-5-applications-django)
4. [Gestion des Rôles & Permissions (RBAC)](#-gestion-des-rôles--permissions-rbac)
5. [Cycles Pédagogiques Maliens](#-cycles-pédagogiques-maliens)
6. [Fonctionnalités Principales](#-fonctionnalités-principales)
7. [Design & Interface Utilisateur](#-design--interface-utilisateur)
8. [Module de Communication Administrative](#-module-de-communication-administrative)
9. [Endpoints API JSON](#-endpoints-api-json)
10. [Installation & Démarrage Rapide](#-installation--démarrage-rapide)
11. [Configuration de l'Environnement (.env)](#-configuration-de-lenvironnement-env)
12. [Comptes de Démonstration](#-comptes-de-démonstration)
13. [Arborescence du Projet](#-arborescence-du-projet)

---

## 🎯 Problématique & Objectifs

Les établissements scolaires font face à des pertes d'informations dues à l'éparpillement des données (inscriptions, notes, présences, règlements de frais).

**SchoolManager résout ce défi en :**
* **Centralisant** l'ensemble des données scolaires sous une base relationnelle unique.
* **Sécurisant** les accès via un contrôle strict par rôle (direction, professeurs, comptables, administrateurs).
* **Automatisant** le calcul des moyennes trimestrielles pondérées et l'édition des bulletins officiels.
* **Simplifiant** le recouvrement des frais de scolarité grâce à un suivi en temps réel et des relances en 1 clic.
* **Respectant** les standards pédagogiques officiels du Mali (DEF, BAC, LMD).

---

## 🧱 Architecture Technique & Modèle Pivot

Le système repose sur le principe fondamental du **modèle pivot `Inscription`** :
* Un **Élève** est inscrit dans une **Classe** pour une **AnnéeScolaire** spécifique.
* Toutes les **Notes**, **Absences** et tous les **Paiements** sont formellement rattachés à cette `Inscription`.
* **Bénéfice immédiat** : Impossibilité absolue de mélanger les notes ou les versements d'années scolaires différentes.

```
[ Établissement ]
       │
[ Année Scolaire ] ──── [ Classe ]
       │                     │
       └───────┬─────────────┘
               ▼
        [ Inscription ]  ◄────── [ Élève ] ◄── M2M ──► [ Parents / Tuteurs ]
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
   [ Note ] [ Absence ] [ Paiement ]
```

---

## 📦 Les 5 Applications Django

| Application | Responsabilités & Modèles |
| :--- | :--- |
| **`accounts`** | Gestion des utilisateurs personnalisés (`CustomUser`), rôles RBAC, décorateurs de sécurité (`@admin_required`, `@direction_required`, etc.), formulaires d'authentification. |
| **`school`** | Établissements, Années scolaires (en cours / archivées), Classes avec niveaux et capacités, Matières et coefficients, Tableau de bord d'accueil (`views_dashboard.py`). |
| **`students`** | Élèves (matricule unique auto-généré), Parents/Tuteurs légaux, ResponsableEleve (relation M2M avec degré de parenté), Inscriptions et suivi des statuts (actif, transféré, exclu). |
| **`academics`** | Enseignants, Affectations (Enseignant ↔ Matière ↔ Classe ↔ Année), Saisie des notes sécurisée par classe, Calcul automatique de moyenne générale pondérée et génération de bulletins imprimables. |
| **`attendance_payments`** | Registre des absences (justifiées ou non), suivi des frais de scolarité, encaissements de paiements, tableau de solvabilité des élèves, services et API d'e-mails transactionnels. |

---

## 🔐 Gestion des Rôles & Permissions (RBAC)

SchoolManager implémente un contrôle d'accès granulaire basé sur le modèle `CustomUser` :

| Rôle | Périmètre & Droits d'accès |
| :--- | :--- |
| **Administrateur** (`admin`) | Accès complet sans restriction : gestion des utilisateurs, des rôles et console Django Admin. |
| **Direction** (`direction`) | Gestion de la structure scolaire, création des classes, matières, affectations d'enseignants, validation des inscriptions. Vue tableau de bord global. |
| **Enseignant** (`enseignant`) | Accès restreint : ne consulte et ne saisit des notes **que pour les classes et matières où il est affecté**. Tableau de bord pédagogique dédié. |
| **Paiement / Intendance** (`paiement`) | Accès financier uniquement : encaissement des paiements, consultation des soldes dus, expédition des relances aux tuteurs. Tableau de bord caisse dédié. |

> 🔒 Chaque tableau de bord n'affiche **que** les sections liées au métier de l'utilisateur connecté — pas de fuite d'information entre rôles.

---

## 📚 Cycles Pédagogiques Maliens

SchoolManager respecte intégralement les normes pédagogiques officielles du Mali :

| Grande Section | Niveaux / Classes |
| :--- | :--- |
| **Maternelle** | Petite Section (PS) · Moyenne Section (MS) · Grande Section (GS) |
| **Fondamental 1er Cycle** | 1ère · 2ème · 3ème · 4ème · 5ème · 6ème année |
| **Fondamental 2nd Cycle** | 7ème · 8ème · 9ème année *(Examen : DEF)* |
| **Lycée** | 10ème · 11ème · Terminale *(Examen : BAC)* |
| **Licence** | Licence 1 · Licence 2 · Licence 3 |
| **Master** | Master 1 · Master 2 |
| **Doctorat** | Doctorat |

> Notes sur 20 · Frais en FCFA · Téléphones au format `+223 XX XX XX XX`

---

## ⚡ Fonctionnalités Principales

### 1. Tableau de bord interactif (`/`)
* Indicateurs clés en temps réel (total élèves, classes actives, professeurs, taux de recouvrement).
* Vue d'ensemble personnalisée selon le rôle de l'utilisateur connecté.
* Horloge dynamique en direct et badge de session sécurisée.
* Accès rapide aux 4 espaces principaux : Statistiques, Carte Scolaire, Documents, Aide.

### 2. Gestion des Élèves & Familles
* Fiche individuelle complète (matricule, photo, niveau, contacts).
* Liaison multi-parents avec degré de parenté et droit de retrait.
* Historique complet des inscriptions sur plusieurs années scolaires.

### 3. Vie Pédagogique
* Saisie des notes avec contrôle strict (0-20) par matière, trimestre et classe affectée.
* Calcul automatique des moyennes pondérées par coefficient.
* Génération et impression des bulletins officiels.
* Registre des absences avec justification et impact statistique.

### 4. Gestion Financière
* Encaissement des frais de scolarité (montant en FCFA).
* Tableau de suivi des soldes en temps réel par classe.
* Relances automatiques par e-mail aux tuteurs des élèves en retard.
* Export des bilans financiers.

### 5. Administration
* Gestion complète des utilisateurs avec attribution de rôles.
* Création des années scolaires, établissements, classes et matières.
* Journal d'actions administratives.
* Console Django Admin accessible aux super-utilisateurs.

### 6. Accessibilité & Responsivité
* Interface 100% responsive (mobile, tablette, desktop).
* Navigation au clavier et aria-live pour les lecteurs d'écran.
* Chargement optimisé pour connexions lentes.
* Messages flash avec disparition automatique après 3 secondes.

---

## 🎨 Design & Interface Utilisateur

### Palette de couleurs
| Rôle | Valeur | Usage |
| :--- | :--- | :--- |
| Charbon exécutif | `#1e2430` | Couleur principale, sidebar |
| Marron terne | `#6b564a` | Accent secondaire, bordures |
| Or pompon | `#c8962d` | Accents or, titres actifs |
| Violet discret | `#6d28d9` | ≤ 15% de la surface totale |
| Vert succès | `#10b981` | Badges, confirmations |

### Page de connexion
* **Arrière-plan** : carrousel de 4 images en fondu enchaîné (5 s par image).
* **Titre rotatif** : 5 phrases animées en cycle toutes les 2 s ("SchoolManager", "Éducation", "Excellence", "Mali 🇲🇱", "Scolaire").
* **Badge** "Pédagogie & Standards Maliens" avec effet shimmer animé.
* **3 cartes glassmorphiques** avec icônes 60×60 et badges de statut.
* **Logo hibou** diplômé officiel (`static/img/logo.jpg`) — format JPG exclusivement.

### Tableaux de bord par rôle
* **Direction** : KPIs globaux, carte scolaire, échanges inter-établissements, statistiques élèves & finances, actualités, calendrier.
* **Enseignant** : classes assignées, matières, notes récentes, absences — rien de financier.
* **Comptable** : encaissements, soldes, recouvrement, inscriptions — rien de pédagogique.

---

## 📧 Module de Communication Administrative

Le service `attendance_payments/services.py` automatise :
* **Relances de paiement** : e-mail personnalisé au tuteur légal dès qu'un solde est impayé au-delà d'un seuil configurable.
* **Convocations parents** : génération d'un document de convocation officiel.
* **Bulletins par e-mail** : envoi du bulletin trimestriel directement aux parents.

Les gabarits HTML des e-mails se trouvent dans `templates/emails/`.

---

## 🌐 Endpoints API JSON

| URL | Description |
| :--- | :--- |
| `/api/stats/` | Statistiques globales (élèves, classes, notes, paiements) |
| `/api/eleves/` | Liste et détail des élèves |
| `/api/notes/` | Notes par inscription, matière ou trimestre |
| `/api/paiements/` | Suivi des paiements et soldes |

Les endpoints sont fournis par **Django REST Framework** (DRF) et nécessitent une authentification par session.

---

## 🚀 Installation & Démarrage Rapide

### Prérequis
* Python 3.10+
* pip / virtualenv
* Git

### Procédure d'installation

1. **Cloner le projet & se positionner dans le répertoire :**
   ```powershell
   cd c:\Users\HP\OneDrive\Desktop\SchoolManager
   ```

2. **Créer et activer l'environnement virtuel :**
   ```powershell
   python -m venv env
   .\env\Scripts\activate
   ```

3. **Installer les dépendances :**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement :**
   ```powershell
   # Copier le fichier exemple et remplir les valeurs
   copy .env.example .env
   # Puis éditer .env avec votre éditeur favori
   ```

5. **Appliquer les migrations de la base de données :**
   ```powershell
   python manage.py migrate
   ```

6. **Charger le jeu de données de test complet :**
   ```powershell
   python manage.py seed_demo
   ```

7. **Lancer le serveur de développement :**
   ```powershell
   python manage.py runserver
   ```

L'application est immédiatement accessible sur : **`http://127.0.0.1:8000/`**

---

## ⚙️ Configuration de l'Environnement (.env)

Copiez `.env.example` en `.env` et renseignez les variables :

```ini
# Sécurité
SECRET_KEY=votre-clé-secrète-django-ici
DEBUG=True

# Base de données (par défaut SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# E-mail (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.com
EMAIL_HOST_PASSWORD=mot-de-passe-application

# Frais scolaires par défaut (FCFA)
FRAIS_SCOLARITE_DEFAULT=50000

# Seuil d'alerte recouvrement (%)
SEUIL_ALERTE_RECOUVREMENT=80
```

> ⚠️ Ne commitez jamais votre fichier `.env` — il est listé dans `.gitignore`.

---

## 🔑 Comptes de Démonstration

La commande `python manage.py seed_demo` pré-remplit la base avec un jeu d'utilisateurs prêts à l'emploi.

> 🔒 **Mot de passe universel pour tous les comptes :** `admin123`

| Identifiant | Rôle | Cas d'usage de test |
| :--- | :--- | :--- |
| **`admin`** | Administrateur Système | Gestion des comptes utilisateurs, accès total et Django Admin (`/admin/`). |
| **`direction`** | Direction des Études | Création de classes, matières, inscriptions et gestion globale des élèves. |
| **`prof_maths`** | Enseignant (M. Dupont) | Saisie des notes de mathématiques pour ses classes affectées (ex: 6ème A). |
| **`comptable`** | Intendance / Paiements | Saisie d'encaissements, suivi des soldes et envoi des relances d'impayés. |

*Astuce* : Sur la page de connexion, **4 boutons d'authentification rapide** permettent de remplir les identifiants d'un simple clic.

---

## 📁 Arborescence du Projet

```text
SchoolManager/
│
├── edumanager/                   # Configuration principale du projet Django
│   ├── settings.py               # Paramètres, barèmes de notes et apps activées
│   ├── urls.py                   # Routeur global vers les applications
│   └── wsgi.py / asgi.py         # Interfaces serveurs
│
├── accounts/                     # Authentification, Rôles & Droits
│   ├── models.py                 # CustomUser avec les 4 rôles RBAC
│   ├── decorators.py             # Décorateurs de sécurité (@direction_required, etc.)
│   ├── views.py / forms.py       # Connexion, déconnexion et gestion des utilisateurs
│   └── urls.py
│
├── school/                       # Établissement, Calendrier & Structure
│   ├── models.py                 # Etablissement, AnneeScolaire, Classe, Matiere
│   ├── views_dashboard.py        # Logique et statistiques du tableau de bord
│   ├── management/commands/      # Commande `seed_demo` pour générer le jeu d'essai
│   └── views.py / forms.py / urls.py
│
├── students/                     # Registre des Élèves & Familles
│   ├── models.py                 # Eleve, Parent, ResponsableEleve, Inscription
│   ├── views.py                  # Annuaire, fiches détaillées, inscriptions
│   └── forms.py / urls.py
│
├── academics/                    # Vie Pédagogique & Évaluations
│   ├── models.py                 # Enseignant, Affectation, Note
│   ├── views.py                  # Saisie des notes, calculs de moyennes et bulletins
│   └── forms.py / urls.py
│
├── attendance_payments/          # Assiduité & Gestion Financière
│   ├── models.py                 # Absence, Paiement, FraisScolaire
│   ├── services.py               # Moteur d'envoi des communications (e-mails / alertes)
│   ├── views.py                  # Suivi des encaissements et endpoints API
│   └── forms.py / urls.py
│
├── templates/                    # Interface utilisateur & Gabarits HTML
│   ├── base.html                 # Gabarit global responsive avec sidebar défilable
│   ├── dashboard.html            # Vue d'accueil avec indicateurs KPI par rôle
│   ├── accounts/                 # login.html (carrousel + titre rotatif), user_list.html
│   ├── school/                   # Listes et formulaires des entités scolaires
│   ├── students/                 # Listes d'élèves, fiche individuelle, parents
│   ├── academics/                # Saisie de notes, affichage et impression du bulletin
│   ├── attendance_payments/      # Registre d'absences, bordereau de suivi des soldes
│   └── emails/                   # Gabarits d'e-mails professionnels (relance, convocation, bulletin)
│
├── static/                       # Ressources statiques
│   ├── css/schoolmanager.css     # Feuille de style personnalisée & barre latérale
│   └── img/logo.jpg              # Logo hibou diplômé officiel (JPG uniquement)
│
├── media/                        # Fichiers uploadés par les utilisateurs (hors git)
│   ├── photos/                   # Photos de profil des élèves et enseignants
│   ├── logos/                    # Logos des établissements
│   └── documents/                # Documents pédagogiques uploadés
│
├── docs/                         # Documentation technique du projet
│   └── screenshots/              # Captures d'écran de référence
│
├── requirements.txt              # Dépendances Python du projet
├── .env.example                  # Modèle de configuration des variables d'environnement
├── .gitignore                    # Fichiers et dossiers exclus du contrôle de version
├── manage.py                     # Utilitaire de commande Django
└── README.md                     # Cette documentation officielle
```

---

## 📦 Dépendances (`requirements.txt`)

```
Django==6.1.3
djangorestframework==3.18.3
Pillow==13.0.0
asgiref==3.13.0
sqlparse==0.6.1
tzdata==2026.6
```

> Pour la production, ajoutez : `gunicorn`, `whitenoise`, `psycopg2-binary`, `django-environ`.

---

## 🛡️ Sécurité & Bonnes Pratiques

* `SECRET_KEY` stockée en variable d'environnement (jamais en dur dans le code).
* `DEBUG=False` obligatoire en production.
* `CSRF_TOKEN` présent sur tous les formulaires POST.
* Permissions vérifiées à chaque vue via décorateurs RBAC.
* Mots de passe hashés avec l'algorithme par défaut de Django (PBKDF2).
* Fichiers `media/` et `db.sqlite3` exclus du dépôt Git via `.gitignore`.

---

*SchoolManager © 2026 — Plateforme d'Excellence & Gestion Scolaire Malienne*
