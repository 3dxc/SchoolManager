import datetime
from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from school.models import Etablissement, AnneeScolaire, Classe, Matiere
from students.models import Eleve, Parent, ResponsableEleve, Inscription
from academics.models import Enseignant, Affectation, Note
from attendance_payments.models import Absence, Paiement


class Command(BaseCommand):
    help = "Génère des données de démonstration complètes pour SchoolManager"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Création des données de test..."))

        # 1. Utilisateurs & Rôles
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'email': 'admin@schoolmanager.local',
                'role': CustomUser.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        direction_user, _ = CustomUser.objects.get_or_create(
            username='direction',
            defaults={
                'first_name': 'Paul',
                'last_name': 'Kouamé',
                'email': 'direction@schoolmanager.local',
                'role': CustomUser.ROLE_DIRECTION,
                'is_staff': True,
            }
        )
        direction_user.set_password('admin123')
        direction_user.save()

        comptable_user, _ = CustomUser.objects.get_or_create(
            username='comptable',
            defaults={
                'first_name': 'Awa',
                'last_name': 'Diop',
                'email': 'comptable@schoolmanager.local',
                'role': CustomUser.ROLE_PAIEMENT,
            }
        )
        comptable_user.set_password('admin123')
        comptable_user.save()

        prof_user, _ = CustomUser.objects.get_or_create(
            username='prof_maths',
            defaults={
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': 'prof_maths@schoolmanager.local',
                'role': CustomUser.ROLE_ENSEIGNANT,
            }
        )
        prof_user.set_password('admin123')
        prof_user.save()

        # 2. Établissement
        etab, _ = Etablissement.objects.get_or_create(
            nom="Groupe Scolaire Excellence",
            defaults={
                'adresse': "Boulevard de la République, Abidjan Plateau",
                'telephone': "+225 07 00 00 00 01",
                'email': "contact@excellence-school.ci",
            }
        )

        # 3. Année Scolaire
        annee, _ = AnneeScolaire.objects.get_or_create(
            etablissement=etab,
            libelle="2024-2025",
            defaults={
                'date_debut': datetime.date(2024, 9, 1),
                'date_fin': datetime.date(2025, 6, 30),
                'statut': AnneeScolaire.STATUT_EN_COURS,
            }
        )

        # 4. Classes
        classe_6a, _ = Classe.objects.get_or_create(nom="6ème A", annee_scolaire=annee, defaults={'niveau': '6e', 'capacite_max': 35})
        classe_5b, _ = Classe.objects.get_or_create(nom="5ème B", annee_scolaire=annee, defaults={'niveau': '5e', 'capacite_max': 35})
        classe_3a, _ = Classe.objects.get_or_create(nom="3ème A", annee_scolaire=annee, defaults={'niveau': '3e', 'capacite_max': 30})

        # 5. Matières
        mat_math, _ = Matiere.objects.get_or_create(nom="Mathématiques", defaults={'coefficient': 3})
        mat_fr, _ = Matiere.objects.get_or_create(nom="Français", defaults={'coefficient': 3})
        mat_ang, _ = Matiere.objects.get_or_create(nom="Anglais", defaults={'coefficient': 2})
        mat_svt, _ = Matiere.objects.get_or_create(nom="Sciences de la Vie et de la Terre", defaults={'coefficient': 2})
        mat_hg, _ = Matiere.objects.get_or_create(nom="Histoire-Géographie", defaults={'coefficient': 2})

        # 6. Enseignants
        ens_math, _ = Enseignant.objects.get_or_create(
            nom="Dupont", prenom="Jean",
            defaults={'specialite': "Mathématiques", 'email': "j.dupont@excellence-school.ci", 'telephone': "+225 01 02 03 04 05", 'user': prof_user}
        )
        ens_fr, _ = Enseignant.objects.get_or_create(
            nom="Bamba", prenom="Mariam",
            defaults={'specialite': "Français", 'email': "m.bamba@excellence-school.ci", 'telephone': "+225 05 06 07 08 09"}
        )

        # 7. Affectations
        Affectation.objects.get_or_create(enseignant=ens_math, matiere=mat_math, classe=classe_6a, annee_scolaire=annee)
        Affectation.objects.get_or_create(enseignant=ens_fr, matiere=mat_fr, classe=classe_6a, annee_scolaire=annee)
        Affectation.objects.get_or_create(enseignant=ens_math, matiere=mat_math, classe=classe_5b, annee_scolaire=annee)

        # 8. Élèves & Parents
        parent1, _ = Parent.objects.get_or_create(
            nom="Koffi", prenom="Auguste",
            defaults={'telephone': "+225 07 11 22 33 44", 'email': "auguste.koffi@gmail.com", 'profession': "Ingénieur"}
        )
        parent2, _ = Parent.objects.get_or_create(
            nom="Traoré", prenom="Fatou",
            defaults={'telephone': "+225 07 55 66 77 88", 'email': "fatou.traore@gmail.com", 'profession': "Médecin"}
        )

        eleve1, _ = Eleve.objects.get_or_create(
            matricule="2024-KOF01",
            defaults={
                'nom': "Koffi", 'prenom': "Marc",
                'date_naissance': datetime.date(2012, 5, 14),
                'sexe': 'M', 'adresse': "Cocody Angré, Abidjan"
            }
        )
        ResponsableEleve.objects.get_or_create(eleve=eleve1, parent=parent1, defaults={'relation': 'pere', 'est_contact_principal': True})

        eleve2, _ = Eleve.objects.get_or_create(
            matricule="2024-TRA02",
            defaults={
                'nom': "Traoré", 'prenom': "Aminata",
                'date_naissance': datetime.date(2013, 2, 20),
                'sexe': 'F', 'adresse': "Marcory Zone 4, Abidjan"
            }
        )
        ResponsableEleve.objects.get_or_create(eleve=eleve2, parent=parent2, defaults={'relation': 'mere', 'est_contact_principal': True})

        # 9. Inscriptions
        ins1, _ = Inscription.objects.get_or_create(
            eleve=eleve1, classe=classe_6a, annee_scolaire=annee,
            defaults={'statut': 'actif', 'frais_scolarite': 180000}
        )
        ins2, _ = Inscription.objects.get_or_create(
            eleve=eleve2, classe=classe_6a, annee_scolaire=annee,
            defaults={'statut': 'actif', 'frais_scolarite': 180000}
        )

        # 10. Paiements
        Paiement.objects.get_or_create(
            reference="PAY-2024-001",
            defaults={
                'inscription': ins1, 'montant': 100000,
                'date': datetime.date(2024, 9, 5), 'mode_paiement': 'especes', 'recu_par': "Awa Diop"
            }
        )
        Paiement.objects.get_or_create(
            reference="PAY-2024-002",
            defaults={
                'inscription': ins2, 'montant': 180000,
                'date': datetime.date(2024, 9, 6), 'mode_paiement': 'mobile_money', 'recu_par': "Awa Diop"
            }
        )

        # 11. Notes
        Note.objects.get_or_create(inscription=ins1, matiere=mat_math, periode='T1', defaults={'valeur': 16.5, 'saisie_par': prof_user})
        Note.objects.get_or_create(inscription=ins1, matiere=mat_fr, periode='T1', defaults={'valeur': 13.0, 'saisie_par': direction_user})
        Note.objects.get_or_create(inscription=ins2, matiere=mat_math, periode='T1', defaults={'valeur': 14.0, 'saisie_par': prof_user})

        # 12. Absences
        Absence.objects.get_or_create(
            inscription=ins1, date=datetime.date(2024, 10, 12),
            defaults={'motif': 'justifie', 'description': "Rendez-vous médical avec certificat."}
        )

        self.stdout.write(self.style.SUCCESS("✓ Données de démonstration créées avec succès !"))
        self.stdout.write(self.style.SUCCESS("Comptes créés (mot de passe : admin123) :"))
        self.stdout.write("  - Admin : 'admin'")
        self.stdout.write("  - Direction : 'direction'")
        self.stdout.write("  - Enseignant : 'prof_maths'")
        self.stdout.write("  - Comptable : 'comptable'")

