from rest_framework import serializers
from accounts.models import CustomUser
from school.models import Etablissement, AnneeScolaire, Classe, Matiere
from students.models import Eleve, Parent, Inscription
from academics.models import Enseignant, Affectation, Note
from attendance_payments.models import Absence, Paiement


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'role_display', 'telephone', 'is_active']


class EtablissementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etablissement
        fields = ['id', 'nom', 'adresse', 'telephone', 'email']


class AnneeScolaireSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = AnneeScolaire
        fields = ['id', 'libelle', 'date_debut', 'date_fin', 'statut', 'statut_display']


class ClasseSerializer(serializers.ModelSerializer):
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)
    nb_eleves = serializers.IntegerField(read_only=True)
    annee_libelle = serializers.CharField(source='annee_scolaire.libelle', read_only=True)
    taux_remplissage = serializers.SerializerMethodField()

    class Meta:
        model = Classe
        fields = ['id', 'nom', 'niveau', 'niveau_display', 'capacite_max', 'nb_eleves', 'annee_scolaire', 'annee_libelle', 'taux_remplissage']

    def get_taux_remplissage(self, obj):
        if obj.capacite_max and obj.capacite_max > 0:
            return round((obj.nb_eleves / obj.capacite_max) * 100, 1)
        return 0


class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'coefficient', 'description']


class EleveSerializer(serializers.ModelSerializer):
    nom_complet = serializers.CharField(read_only=True)
    sexe_display = serializers.CharField(source='get_sexe_display', read_only=True)

    class Meta:
        model = Eleve
        fields = ['id', 'matricule', 'nom', 'prenom', 'nom_complet', 'date_naissance', 'sexe', 'sexe_display', 'adresse']


class InscriptionSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom_complet', read_only=True)
    eleve_matricule = serializers.CharField(source='eleve.matricule', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    annee_libelle = serializers.CharField(source='annee_scolaire.libelle', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    montant_paye = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    solde_restant = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    est_a_jour = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inscription
        fields = [
            'id', 'eleve', 'eleve_nom', 'eleve_matricule', 'classe', 'classe_nom',
            'annee_scolaire', 'annee_libelle', 'statut', 'statut_display',
            'frais_scolarite', 'montant_paye', 'solde_restant', 'est_a_jour'
        ]


class NoteSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='inscription.eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='inscription.classe.nom', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    periode_display = serializers.CharField(source='get_periode_display', read_only=True)
    saisie_par_nom = serializers.CharField(source='saisie_par.get_full_name', read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'inscription', 'eleve_nom', 'classe_nom', 'matiere', 'matiere_nom',
            'periode', 'periode_display', 'valeur', 'commentaire', 'saisie_par_nom', 'updated_at'
        ]


class PaiementSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='inscription.eleve.nom_complet', read_only=True)
    eleve_matricule = serializers.CharField(source='inscription.eleve.matricule', read_only=True)
    classe_nom = serializers.CharField(source='inscription.classe.nom', read_only=True)
    mode_display = serializers.CharField(source='get_mode_paiement_display', read_only=True)

    class Meta:
        model = Paiement
        fields = [
            'id', 'reference', 'inscription', 'eleve_nom', 'eleve_matricule',
            'classe_nom', 'montant', 'date', 'mode_paiement', 'mode_display', 'recu_par'
        ]


class AbsenceSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='inscription.eleve.nom_complet', read_only=True)
    classe_nom = serializers.CharField(source='inscription.classe.nom', read_only=True)
    motif_display = serializers.CharField(source='get_motif_display', read_only=True)

    class Meta:
        model = Absence
        fields = ['id', 'inscription', 'eleve_nom', 'classe_nom', 'date', 'motif', 'motif_display', 'description']


# ── Serializers d'actions rapides (Fast mutation API) ─────────────────────────
class QuickNoteInputSerializer(serializers.Serializer):
    inscription_id = serializers.IntegerField()
    matiere_id = serializers.IntegerField()
    periode = serializers.CharField(max_length=5)
    valeur = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=20)
    commentaire = serializers.CharField(max_length=200, required=False, allow_blank=True)


class QuickPaiementInputSerializer(serializers.Serializer):
    inscription_id = serializers.IntegerField()
    montant = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    mode_paiement = serializers.ChoiceField(choices=Paiement.MODE_CHOICES, default=Paiement.MODE_ESPECES)
    date = serializers.DateField(required=False)
    recu_par = serializers.CharField(max_length=100, required=False, allow_blank=True)
    observations = serializers.CharField(required=False, allow_blank=True)

