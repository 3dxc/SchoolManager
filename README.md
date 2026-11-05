# 🎓 SchoolManager — Système Intégré de Gestion Scolaire

**SchoolManager** est une solution web complète, moderne et responsive développée avec le framework **Django**. Elle centralise la gestion administrative, pédagogique et financière des établissements d'enseignement primaire et secondaire.

---

## 📑 Table des matières

1. [Problématique & Objectifs](#-problématique--objectifs)
2. [Architecture Technique & Modèle Pivot](#-architecture-technique--modèle-pivot)
3. [Les 5 Applications Django](#-les-5-applications-django)
4. [Gestion des Rôles & Permissions (RBAC)](#-gestion-des-rôles--permissions-rbac)
5. [Fonctionnalités Principales](#-fonctionnalités-principales)
6. [Module de Communication Administrative](#-module-de-communication-administrative)
7. [Endpoints API JSON](#-endpoints-api-json)
8. [Installation & Démarrage Rapide](#-installation--démarrage-rapide)
9. [Comptes de Démonstration](#-comptes-de-démonstration)
10. [Arborescence du Projet](#-arborescence-du-projet)

---

## 🎯 Problématique & Objectifs

Les établissements scolaires font face à des pertes d'informations dues à l'éparpillement des données (inscriptions, notes, présences, règlements de frais). 

**SchoolManager résout ce défi en :**
* **Centralisant** l'ensemble des données scolaires sous une base relationnelle unique.
* **Sécurisant** les accès via un contrôle strict par rôle (direction, professeurs, comptables, administrateurs).
* **Automatisant** le calcul des moyennes trimestrielles pondérées et l'édition des bulletins officiels.
* **Simplifiant** le recouvrement des frais de scolarité grâce à un suivi en temps réel et des relances en 1 clic.

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
| **Direction** (`direction`) | Gestion de la structure scolaire, création des classes, matières, affectations d'enseignants, validation des inscriptions. |
| **Enseignant** (`enseignant`) | Accès restreint : ne consulte et ne saisit des notes **que pour les classes et matières où il est affecté**. |
| **Paiement / Intendance** (`paiement`) | Accès financier : encaissement des paiements, consultation des soldes dus, expédition des relances aux tuteurs. |

---

## ⚡ Fonctionnalités Principales

### 1. Tableau de bord interactif (`/`)
* Indicateurs clés en temps réel (total élèves, classes actives, professeurs, inscriptions actives).
* Vue d'ensemble des dernières opérations financières.
* Raccourcis rapides d'actions fréquentes.

### 2. Gestion des Élèves & Tuteurs (`/students/`)
* Attribution automatique d'un matricule scolaire unique (`AAAA-XXXXXX`).
* Fiche détaillée par élève : historique de toutes ses inscriptions, coordonnées des parents avec mention du contact principal.
* Recherche et filtrage multi-critères (nom, prénom, matricule).

### 3. Pédagogie, Saisie des Notes & Bulletins (`/academics/`)
* **Affectations strictes** : un enseignant n'intervient que dans son périmètre assigné.
* **Saisie des notes** : contrôle automatique du barème (0 à 20 par défaut, configurable dans `settings.py`).
* **Bulletin scolaire officiel** :
  * Calcul automatique de la moyenne par matière.
  * Application des coefficients respectifs.
  * Calcul de la moyenne générale pondérée.
  * Récapitulatif des absences de la période.
  * Mise en page optimisée pour l'impression papier (`window.print()`).

### 4. Absences & Frais Scolaires (`/attendance/`)
* Suivi des absences avec distinction (justifiée avec motif / non justifiée).
* Suivi de solvabilité (`/attendance/paiements/suivi/`) : identification immédiate des élèves à jour ou en retard de paiement.
* Génération automatique de références de reçu uniques (`PAY-XXXXXXXX`).

---

## ✉️ Module de Communication Administrative

L'application intègre des gabarits HTML transactionnels soignés et réutilisables (`templates/emails/`) :

1. **Relance d'impayé de scolarité** (`relance_paiement.html`) : Rappel bienveillant ou formel du solde restant et des modalités de versement.
2. **Convocation de parent / tuteur** (`convocation_parent.html`) : Invitation à un entretien pédagogique ou disciplinaire avec date, heure et interlocuteurs.
3. **Notification de bulletin** (`bulletin_notification.html`) : Annonce aux familles de la mise à disposition des résultats scolaires avec résumé des performances.

> **Déclenchement en 1 clic** :
> * Bouton **"Envoyer relance"** sur la liste des soldes impayés.
> * Bouton **"Notifier le tuteur"** directement sur la page du bulletin.

---

## 🔌 Endpoints API JSON

Des services API sont exposés pour automatiser les interactions avec des systèmes tiers ou des scripts d'automatisation :

### 1. Déclencher une relance de frais de scolarité
* **Route** : `POST /attendance/api/relance/<inscription_id>/`
* **Corps JSON optionnel** :
  ```json
  {
    "date_echeance": "30 novembre 2024"
  }
  ```
* **Réponse** :
  ```json
  {
    "status": "success",
    "message": "Notification de relance transmise avec succès à parent@email.com.",
    "solde_restant": 80000.0
  }
  ```

### 2. Déclencher une convocation de parent
* **Route** : `POST /attendance/api/convocation/<inscription_id>/`
* **Corps JSON** :
  ```json
  {
    "date_rdv": "2024-11-25",
    "heure_rdv": "10h00",
    "motif": "Entretien de suivi trimestriel",
    "interlocuteurs": "Direction & Professeur Principal"
  }
  ```

---

## 🚀 Installation & Démarrage Rapide

### Prérequis
* Python 3.10 ou supérieur
* Git

### Procédure d'installation

1. **Cloner le projet & se positionner dans le répertoire :**
   ```powershell
   cd c:\Users\HP\OneDrive\Desktop\SchoolManager
   ```

2. **Activer l'environnement virtuel :**
   ```powershell
   .\env\Scripts\activate
   ```

3. **Appliquer les migrations de la base de données :**
   ```powershell
   python manage.py migrate
   ```

4. **Charger le jeu de données de test complet :**
   ```powershell
   python manage.py seed_demo
   ```

5. **Lancer le serveur de développement :**
   ```powershell
   python manage.py runserver
   ```

L'application est immédiatement accessible sur : **`http://127.0.0.1:8000/`**

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
│   ├── dashboard.html            # Vue d'accueil avec indicateurs
│   ├── accounts/                 # login.html, user_list.html, user_form.html
│   ├── school/                   # Listes et formulaires des entités scolaires
│   ├── students/                 # Listes d'élèves, fiche individuelle, parents
│   ├── academics/                # Saisie de notes, affichage et impression du bulletin
│   ├── attendance_payments/      # Registre d'absences, bordereau de suivi des soldes
│   └── emails/                   # Gabarits d'e-mails professionnels (relance, convocation, bulletin)
│
├── static/                       # Ressources statiques
│   └── css/schoolmanager.css     # Feuille de style personnalisée & barre latérale
│
├── manage.py                     # Utilitaire de commande Django
└── README.md                     # Documentation officielle du projet
```
