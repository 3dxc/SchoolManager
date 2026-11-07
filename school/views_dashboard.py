import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum

from school.models import Etablissement, AnneeScolaire, Classe, Matiere
from students.models import Eleve, Inscription
from academics.models import Enseignant, Affectation, Note
from attendance_payments.models import Paiement, Absence


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    # ════════════════════════════════════════════════════════════════════════
    # 1. ESPACE ENSEIGNANT (Uniquement les sections liées à la pédagogie)
    # ════════════════════════════════════════════════════════════════════════
    if user.is_enseignant:
        # Trouver le profil enseignant s'il existe
        ens_profil = getattr(user, 'enseignant_profil', None)
        if ens_profil:
            affectations_qs = Affectation.objects.filter(enseignant=ens_profil).select_related('classe', 'matiere', 'annee_scolaire')
            notes_qs = Note.objects.filter(saisie_par=user).select_related('inscription__eleve', 'matiere')
        else:
            affectations_qs = Affectation.objects.all().select_related('classe', 'matiere', 'annee_scolaire')
            notes_qs = Note.objects.all().select_related('inscription__eleve', 'matiere')

        classes_ids = list(affectations_qs.values_list('classe_id', flat=True))
        eleves_count = Inscription.objects.filter(classe_id__in=classes_ids, statut='actif').count()
        if not eleves_count:
            eleves_count = Eleve.objects.count()

        context.update({
            'nb_classes_assignees': affectations_qs.values('classe_id').distinct().count() or Classe.objects.count(),
            'nb_matieres_assignees': affectations_qs.values('matiere_id').distinct().count() or Matiere.objects.count(),
            'nb_notes_saisies': notes_qs.count() or Note.objects.count(),
            'nb_eleves_total': eleves_count,
            'mes_affectations': affectations_qs[:8],
            'mes_notes_recentes': notes_qs.order_by('-created_at')[:8],
            'absences_recentes': Absence.objects.select_related('inscription__eleve').order_by('-date')[:6],
        })
        return render(request, 'dashboard.html', context)

    # ════════════════════════════════════════════════════════════════════════
    # 2. ESPACE COMPTABLE / CAISSE (Uniquement les sections liées aux finances)
    # ════════════════════════════════════════════════════════════════════════
    if user.is_paiement:
        total_encaisse = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
        inscriptions_actives = Inscription.objects.filter(statut='actif').count()
        frais_moyen_estime = 150000  # FCFA
        total_previsionnel = max(total_encaisse, inscriptions_actives * frais_moyen_estime)
        reste_a_recouvrer = max(0, total_previsionnel - total_encaisse)
        taux_recouvrement = round((total_encaisse / total_previsionnel * 100) if total_previsionnel else 0, 1)

        context.update({
            'total_encaisse': total_encaisse,
            'total_previsionnel': total_previsionnel,
            'reste_a_recouvrer': reste_a_recouvrer,
            'taux_recouvrement': taux_recouvrement,
            'nb_quittances': Paiement.objects.count(),
            'nb_inscriptions': inscriptions_actives,
            'derniers_paiements': Paiement.objects.select_related('inscription__eleve').order_by('-date')[:12],
            'inscriptions_suivi': Inscription.objects.select_related('eleve', 'classe').all()[:8],
        })
        return render(request, 'dashboard.html', context)

    # ════════════════════════════════════════════════════════════════════════
    # 3. ESPACE DIRECTION & ADMINISTRATEUR (Vue stratégique & complète)
    # ════════════════════════════════════════════════════════════════════════
    directions_list = [
        {
            'code': 'AMALAN',
            'nom': 'Académie Malienne des Langues',
            'email': 'amalan@porteduc.ml',
            'telephone': '+223 20 22 28 36',
        },
        {
            'code': 'CAB',
            'nom': 'Cabinet & Direction Générale',
            'email': 'cab@porteduc.ml',
            'telephone': '+223 20 23 10 35',
        },
        {
            'code': 'CPS',
            'nom': 'Cellule de Planification et de Statistique',
            'email': 'cps@porteduc.ml',
            'telephone': '+223 20 22 54 89',
        },
        {
            'code': 'DNEF',
            'nom': 'Direction Nationale de l’Enseignement',
            'email': 'dnef@porteduc.ml',
            'telephone': '+223 20 22 41 77',
        },
    ]

    total_eleves = Eleve.objects.count()
    nb_garcons = Eleve.objects.filter(sexe='M').count()
    nb_filles = Eleve.objects.filter(sexe='F').count()
    pourcent_garcons = round((nb_garcons / total_eleves * 100) if total_eleves else 50, 1)
    pourcent_filles = round((nb_filles / total_eleves * 100) if total_eleves else 50, 1)

    total_encaisse = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
    inscriptions_actives = Inscription.objects.filter(statut='actif').count()
    frais_moyen_estime = 150000
    total_previsionnel = max(total_encaisse, inscriptions_actives * frais_moyen_estime)
    reste_a_recouvrer = max(0, total_previsionnel - total_encaisse)
    taux_recouvrement = round((total_encaisse / total_previsionnel * 100) if total_previsionnel else 0, 1)

    echanges_etablissements = [
        {
            'id': 'TR-2026-08',
            'eleve_nom': 'Traoré Aminata',
            'classe': 'Terminale S',
            'origine': 'Enko Bamako Campus 1',
            'destination': 'Lycée Ba Aminata Diallo',
            'motif': 'Déménagement familial & Cursus Scientifique',
            'statut': 'valide',
            'date': '04 Nov 2026'
        },
        {
            'id': 'TR-2026-09',
            'eleve_nom': 'Coulibaly Ibrahim',
            'classe': '1ère ES',
            'origine': 'Lycée Castors',
            'destination': 'TechnoLab Insta',
            'motif': 'Orientation Baccalauréat International (IB)',
            'statut': 'en_cours',
            'date': '06 Nov 2026'
        },
        {
            'id': 'TR-2026-10',
            'eleve_nom': 'Diallo Fatoumata',
            'classe': '3ème Année Superieur',
            'origine': 'Complexe Scolaire Progrès',
            'destination': 'SchoolManager Pilote Bamako',
            'motif': 'Rapprochement du domicile parental',
            'statut': 'en_attente',
            'date': '06 Nov 2026'
        },
    ]

    # Répartition par grand cycle pédagogique
    cycles_breakdown = [
        {'id': 'maternelle', 'label': 'Maternelle (PS, MS, GS)', 'nb': Classe.objects.filter(grande_section='maternelle').count(), 'icone': 'bi-balloon'},
        {'id': 'fondamental_1', 'label': '1er Cycle Fondamental (1ère à 6ème)', 'nb': Classe.objects.filter(grande_section='fondamental_1').count(), 'icone': 'bi-book'},
        {'id': 'fondamental_2', 'label': '2nd Cycle Fondamental (7ème à 9ème DEF)', 'nb': Classe.objects.filter(grande_section='fondamental_2').count(), 'icone': 'bi-award'},
        {'id': 'lycee', 'label': 'Lycée (10ème, 11ème, Terminale BAC)', 'nb': Classe.objects.filter(grande_section='lycee').count(), 'icone': 'bi-mortarboard'},
        {'id': 'superieur', 'label': 'Enseignement Supérieur (LMD Licence/Master)', 'nb': Classe.objects.filter(grande_section__in=['licence', 'master', 'doctorat']).count(), 'icone': 'bi-bank'},
    ]

    actualites_academie = [
        {
            'date': '05 Nov 2026',
            'titre': 'Calendrier officiel des examens du DEF et du Baccalauréat session 2026 publié',
            'source': 'Ministère de l’Éducation Nationale',
            'tag': 'Examens Nationaux',
            'badge': 'bg-danger bg-opacity-10 text-danger border-danger border-opacity-25'
        },
        {
            'date': '02 Nov 2026',
            'titre': 'Déploiement du module de relevés numériques et quittances sécurisées avec QR Code',
            'source': 'Cellule Informatique & Statistiques (CPS)',
            'tag': 'Innovation',
            'badge': 'bg-success bg-opacity-10 text-success border-success border-opacity-25'
        },
        {
            'date': '28 Oct 2026',
            'titre': 'Convention de mobilité inter-établissements validée pour les élèves en transfert',
            'source': 'Direction Nationale des Enseignements',
            'tag': 'Partenariat',
            'badge': 'bg-primary bg-opacity-10 text-primary border-primary border-opacity-25'
        }
    ]

    calendrier_scolaire = [
        {'date': '15 Octobre', 'evenement': 'Rentrée solennelle & Démarrage des enseignements', 'statut': 'Terminé', 'badge': 'bg-secondary'},
        {'date': '20 Décembre', 'evenement': 'Arrêt des notes du 1er Trimestre & Conseils de classe', 'statut': 'En cours', 'badge': 'bg-warning text-dark'},
        {'date': '24 Déc. - 05 Jan.', 'evenement': 'Congés du 1er Trimestre & Fêtes de fin d\'année', 'statut': 'À venir', 'badge': 'bg-light text-dark border'},
        {'date': '15 - 20 Mars', 'evenement': 'Examens blancs préparatoires DEF & BAC', 'statut': 'À venir', 'badge': 'bg-light text-dark border'},
        {'date': '01 - 04 Juin', 'evenement': 'Épreuves nationales du Diplôme d’Études Fondamentales (DEF)', 'statut': 'Session 2026', 'badge': 'bg-info bg-opacity-20 text-dark'},
        {'date': '15 - 19 Juin', 'evenement': 'Épreuves nationales du Baccalauréat Malien (BAC)', 'statut': 'Session 2026', 'badge': 'bg-primary bg-opacity-20 text-primary'},
    ]

    context.update({
        'nb_eleves': total_eleves,
        'nb_garcons': nb_garcons,
        'nb_filles': nb_filles,
        'pourcent_garcons': pourcent_garcons,
        'pourcent_filles': pourcent_filles,
        'nb_classes': Classe.objects.count(),
        'nb_enseignants': Enseignant.objects.count(),
        'nb_inscriptions_actives': inscriptions_actives,
        'annees': AnneeScolaire.objects.select_related('etablissement').all()[:5],
        'derniers_paiements': Paiement.objects.select_related('inscription__eleve').order_by('-date')[:5],
        'etablissements': Etablissement.objects.all()[:4],
        'total_encaisse': total_encaisse,
        'total_previsionnel': total_previsionnel,
        'reste_a_recouvrer': reste_a_recouvrer,
        'taux_recouvrement': taux_recouvrement,
        'echanges_etablissements': echanges_etablissements,
        'directions': directions_list,
        'cycles_breakdown': cycles_breakdown,
        'actualites_academie': actualites_academie,
        'calendrier_scolaire': calendrier_scolaire,
        'stats_excellence': {
            'admis_universite': 118,
            'anciens_reseau': '1 500+',
            'pays_etudes': 30,
            'enseignants_certifies': '50+',
            'taux_reussite': '98%',
        }
    })
    return render(request, 'dashboard.html', context)


@login_required
def export_stats_csv(request):
    """
    Génère et télécharge un fichier CSV complet des statistiques
    élèves et financières de l'établissement.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    filename = f"rapport_statistiques_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response, delimiter=';')

    writer.writerow(["RÉPUBLIQUE DU MALI - MINISTÈRE DE L'ÉDUCATION NATIONALE"])
    writer.writerow(["SCHOOLMANAGER - RAPPORT OFFICIEL ET BILAN FINANCIER"])
    writer.writerow([f"Date d'extraction : {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}"])
    writer.writerow([f"Généré par : {request.user.get_full_name() or request.user.username} ({request.user.get_role_display()})"])
    writer.writerow([])

    # 1. Statistiques Élèves
    writer.writerow(["=== 1. STATISTIQUES DES ÉLÈVES ==="])
    writer.writerow(["Indicateur", "Valeur"])
    total_eleves = Eleve.objects.count()
    nb_garcons = Eleve.objects.filter(sexe='M').count()
    nb_filles = Eleve.objects.filter(sexe='F').count()
    inscrits_actifs = Inscription.objects.filter(statut='actif').count()
    writer.writerow(["Total élèves enregistrés", total_eleves])
    writer.writerow(["Garçons (M)", f"{nb_garcons} ({(nb_garcons/total_eleves*100 if total_eleves else 0):.1f}%)"])
    writer.writerow(["Filles (F)", f"{nb_filles} ({(nb_filles/total_eleves*100 if total_eleves else 0):.1f}%)"])
    writer.writerow(["Inscriptions actives", inscrits_actifs])
    writer.writerow(["Classes ouvertes", Classe.objects.count()])
    writer.writerow(["Enseignants actifs", Enseignant.objects.count()])
    writer.writerow([])

    # 2. Statistiques Financières
    writer.writerow(["=== 2. BILAN FINANCIER ==="])
    total_encaisse = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
    total_prev = max(total_encaisse, inscrits_actifs * 150000)
    reste = max(0, total_prev - total_encaisse)
    taux = (total_encaisse / total_prev * 100) if total_prev else 0
    writer.writerow(["Indicateur", "Montant (FCFA)"])
    writer.writerow(["Total Encaissé", f"{total_encaisse:.0f} FCFA"])
    writer.writerow(["Total Prévisionnel", f"{total_prev:.0f} FCFA"])
    writer.writerow(["Reste à Recouvrer", f"{reste:.0f} FCFA"])
    writer.writerow(["Taux de Recouvrement", f"{taux:.1f} %"])
    writer.writerow([])

    # 3. Derniers paiements
    writer.writerow(["=== 3. JOURNAL DES DERNIERS PAIEMENTS ==="])
    writer.writerow(["Référence", "Date", "Élève", "Montant (FCFA)", "Mode"])
    for p in Paiement.objects.select_related('inscription__eleve').order_by('-date')[:25]:
        writer.writerow([
            p.reference,
            p.date.strftime('%d/%m/%Y'),
            str(p.inscription.eleve),
            f"{p.montant:.0f}",
            p.get_mode_display() if hasattr(p, 'get_mode_display') else 'Caisse'
        ])

    return response
