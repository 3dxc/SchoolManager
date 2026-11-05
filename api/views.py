import datetime
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from accounts.models import CustomUser
from school.models import Etablissement, AnneeScolaire, Classe, Matiere
from students.models import Eleve, Inscription
from academics.models import Enseignant, Affectation, Note
from attendance_payments.models import Absence, Paiement
from .serializers import (
    UserSerializer, ClasseSerializer, InscriptionSerializer,
    NoteSerializer, PaiementSerializer, AbsenceSerializer,
    QuickNoteInputSerializer, QuickPaiementInputSerializer
)


class DashboardStatsAPIView(APIView):
    """
    Retourne les statistiques clés temps-réel adaptées au rôle de l'utilisateur connecté.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        base_stats = {
            'role': user.role,
            'role_display': user.get_role_display(),
            'user_name': user.get_full_name() or user.username,
        }

        if user.is_admin:
            base_stats.update({
                'nb_utilisateurs': CustomUser.objects.count(),
                'nb_eleves': Eleve.objects.count(),
                'nb_classes': Classe.objects.count(),
                'nb_enseignants': Enseignant.objects.count(),
                'total_recouvre': float(Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0),
            })
        elif user.is_direction:
            base_stats.update({
                'nb_eleves': Eleve.objects.count(),
                'nb_classes': Classe.objects.count(),
                'nb_inscriptions_actives': Inscription.objects.filter(statut='actif').count(),
                'nb_enseignants': Enseignant.objects.count(),
            })
        elif user.is_enseignant and hasattr(user, 'enseignant_profil'):
            ens = user.enseignant_profil
            affs = Affectation.objects.filter(enseignant=ens)
            classes_ids = affs.values_list('classe_id', flat=True)
            base_stats.update({
                'nb_classes_assignees': affs.values('classe_id').distinct().count(),
                'nb_matieres_assignees': affs.values('matiere_id').distinct().count(),
                'nb_eleves_total': Inscription.objects.filter(classe_id__in=classes_ids, statut='actif').count(),
                'nb_notes_saisies': Note.objects.filter(saisie_par=user).count(),
            })
        elif user.is_paiement:
            total_paye = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
            total_frais = Inscription.objects.filter(statut='actif').aggregate(total=Sum('frais_scolarite'))['total'] or 0
            solde_du = max(0, total_frais - total_paye)
            taux = round((total_paye / total_frais * 100), 1) if total_frais > 0 else 0
            base_stats.update({
                'total_recouvre': float(total_paye),
                'total_a_recouvrer': float(solde_du),
                'taux_recouvrement': taux,
                'nb_paiements': Paiement.objects.count(),
            })

        return Response(base_stats)


class DirectionWorkspaceAPIView(APIView):
    """
    Fournit les données complètes du tableau de bord de la Direction.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_direction and not request.user.is_admin:
            return Response({'detail': 'Accès non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        annee_active = AnneeScolaire.objects.filter(statut='en_cours').first()
        classes = Classe.objects.filter(annee_scolaire=annee_active) if annee_active else Classe.objects.all()
        inscriptions_recentes = Inscription.objects.select_related('eleve', 'classe').order_by('-created_at')[:8]

        data = {
            'annee_en_cours': annee_active.libelle if annee_active else "Aucune année active",
            'classes': ClasseSerializer(classes, many=True).data,
            'inscriptions_recentes': InscriptionSerializer(inscriptions_recentes, many=True).data,
            'total_eleves': Eleve.objects.count(),
            'total_classes': classes.count(),
            'total_enseignants': Enseignant.objects.count(),
        }
        return Response(data)


class EnseignantWorkspaceAPIView(APIView):
    """
    Fournit les données spécifiques à l'espace de travail d'un Enseignant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_enseignant and not request.user.is_admin:
            return Response({'detail': 'Accès non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        ens_profil = getattr(request.user, 'enseignant_profil', None)
        if not ens_profil and not request.user.is_admin:
            return Response({'detail': 'Aucun profil enseignant associé.'}, status=status.HTTP_404_NOT_FOUND)

        affs = Affectation.objects.filter(enseignant=ens_profil) if ens_profil else Affectation.objects.all()
        classes_ids = affs.values_list('classe_id', flat=True)
        inscriptions = Inscription.objects.filter(classe_id__in=classes_ids, statut='actif').select_related('eleve', 'classe')
        notes_recentes = Note.objects.filter(matiere__in=affs.values_list('matiere_id', flat=True)).select_related('inscription__eleve', 'matiere').order_by('-updated_at')[:8]

        affectations_data = []
        for aff in affs.select_related('matiere', 'classe', 'annee_scolaire'):
            affectations_data.append({
                'id': aff.id,
                'classe_id': aff.classe.id,
                'classe_nom': aff.classe.nom,
                'matiere_id': aff.matiere.id,
                'matiere_nom': aff.matiere.nom,
                'nb_eleves': aff.classe.nb_eleves,
                'annee': aff.annee_scolaire.libelle,
            })

        return Response({
            'enseignant_nom': ens_profil.nom_complet if ens_profil else request.user.get_full_name(),
            'specialite': ens_profil.specialite if ens_profil else "Toutes",
            'affectations': affectations_data,
            'eleves': InscriptionSerializer(inscriptions[:30], many=True).data,
            'notes_recentes': NoteSerializer(notes_recentes, many=True).data,
        })


class ComptableWorkspaceAPIView(APIView):
    """
    Fournit les données financières pour l'espace comptable.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_paiement and not request.user.is_admin:
            return Response({'detail': 'Accès non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        paiements_recents = Paiement.objects.select_related('inscription__eleve', 'inscription__classe').order_by('-date', '-created_at')[:8]
        inscriptions = Inscription.objects.filter(statut='actif').select_related('eleve', 'classe')

        # Identifier les élèves en retard
        retards = [ins for ins in inscriptions if not ins.est_a_jour][:8]

        total_paye = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
        total_frais = inscriptions.aggregate(total=Sum('frais_scolarite'))['total'] or 0
        solde_restant = max(0, total_frais - total_paye)

        return Response({
            'total_encaisse': float(total_paye),
            'solde_restant_global': float(solde_restant),
            'paiements_recents': PaiementSerializer(paiements_recents, many=True).data,
            'eleves_en_retard': InscriptionSerializer(retards, many=True).data,
            'nb_eleves_a_jour': len([ins for ins in inscriptions if ins.est_a_jour]),
            'nb_eleves_en_retard': len(retards),
        })


# ── Actions Rapides Interactives (POST) ───────────────────────────────────────
class QuickNoteAPIView(APIView):
    """
    API permettant d'enregistrer instantanément une note depuis le tableau de bord enseignant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not (request.user.is_enseignant or request.user.is_admin or request.user.is_direction):
            return Response({'detail': 'Permission refusée.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuickNoteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        try:
            inscription = Inscription.objects.get(pk=d['inscription_id'])
            matiere = Matiere.objects.get(pk=d['matiere_id'])
        except (Inscription.DoesNotExist, Matiere.DoesNotExist):
            return Response({'detail': 'Élève ou matière introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Création ou mise à jour
        note, created = Note.objects.update_or_create(
            inscription=inscription,
            matiere=matiere,
            periode=d['periode'],
            defaults={
                'valeur': d['valeur'],
                'commentaire': d.get('commentaire', ''),
                'saisie_par': request.user,
            }
        )

        return Response({
            'status': 'success',
            'action': 'created' if created else 'updated',
            'message': f"Note de {note.valeur}/20 enregistrée pour {inscription.eleve.nom_complet}.",
            'note': NoteSerializer(note).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class QuickPaiementAPIView(APIView):
    """
    API permettant d'enregistrer un encaissement express depuis le tableau de bord comptable.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not (request.user.is_paiement or request.user.is_admin or request.user.is_direction):
            return Response({'detail': 'Permission refusée.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuickPaiementInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        try:
            inscription = Inscription.objects.get(pk=d['inscription_id'])
        except Inscription.DoesNotExist:
            return Response({'detail': 'Inscription introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        paiement = Paiement.objects.create(
            inscription=inscription,
            montant=d['montant'],
            date=d.get('date', datetime.date.today()),
            mode_paiement=d['mode_paiement'],
            recu_par=d.get('recu_par') or request.user.get_full_name() or request.user.username,
            observations=d.get('observations', '')
        )

        return Response({
            'status': 'success',
            'message': f"Paiement de {paiement.montant} FCFA enregistré sous la référence {paiement.reference}.",
            'solde_restant': float(inscription.solde_restant),
            'paiement': PaiementSerializer(paiement).data
        }, status=status.HTTP_201_CREATED)
