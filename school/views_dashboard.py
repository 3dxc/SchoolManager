from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from school.models import Etablissement, AnneeScolaire, Classe
from students.models import Eleve, Inscription
from academics.models import Enseignant
from attendance_payments.models import Paiement


@login_required
def dashboard(request):
    context = {
        'nb_eleves': Eleve.objects.count(),
        'nb_classes': Classe.objects.count(),
        'nb_enseignants': Enseignant.objects.count(),
        'nb_inscriptions_actives': Inscription.objects.filter(statut='actif').count(),
        'annees': AnneeScolaire.objects.select_related('etablissement').all()[:5],
        'derniers_paiements': Paiement.objects.select_related('inscription__eleve').order_by('-date')[:5],
    }
    return render(request, 'dashboard.html', context)
