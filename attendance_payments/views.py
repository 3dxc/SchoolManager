from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Absence, Paiement
from .forms import AbsenceForm, PaiementForm
from .services import envoyer_relance_paiement, envoyer_convocation_parent
from students.models import Inscription
from school.models import AnneeScolaire
from accounts.decorators import enseignant_required, paiement_required, direction_required


# ── Absences ──────────────────────────────────────────────────────────────────
@login_required
@enseignant_required
def absence_list(request):
    annee_pk = request.GET.get('annee')
    q = request.GET.get('q', '')
    absences = Absence.objects.select_related('inscription__eleve', 'inscription__classe', 'inscription__annee_scolaire')
    # Enseignant ne voit que ses classes
    if request.user.role == 'enseignant' and hasattr(request.user, 'enseignant_profil'):
        enseignant = request.user.enseignant_profil
        from academics.models import Affectation
        affectations = Affectation.objects.filter(enseignant=enseignant)
        classes = affectations.values_list('classe', flat=True)
        annees = affectations.values_list('annee_scolaire', flat=True)
        absences = absences.filter(inscription__classe__in=classes, inscription__annee_scolaire__in=annees)
    if annee_pk:
        absences = absences.filter(inscription__annee_scolaire__pk=annee_pk)
    if q:
        absences = absences.filter(
            Q(inscription__eleve__nom__icontains=q) | Q(inscription__eleve__prenom__icontains=q)
        )
    annees = AnneeScolaire.objects.all()
    return render(request, 'attendance_payments/absence_list.html', {
        'absences': absences, 'annees': annees, 'annee_active': annee_pk, 'q': q
    })


@login_required
@enseignant_required
def absence_create(request):
    form = AbsenceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            abs_ = form.save(commit=False)
            abs_.full_clean()
            abs_.save()
            messages.success(request, 'Absence enregistrée.')
            return redirect('attendance_payments:absence_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'attendance_payments/absence_form.html', {'form': form, 'title': 'Enregistrer une absence'})


@login_required
@enseignant_required
def absence_edit(request, pk):
    obj = get_object_or_404(Absence, pk=pk)
    form = AbsenceForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Absence mise à jour.')
        return redirect('attendance_payments:absence_list')
    return render(request, 'attendance_payments/absence_form.html', {
        'form': form, 'title': 'Modifier l\'absence', 'object': obj
    })


@login_required
@enseignant_required
def absence_delete(request, pk):
    obj = get_object_or_404(Absence, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Absence supprimée.')
        return redirect('attendance_payments:absence_list')
    return render(request, 'attendance_payments/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'absence'})


# ── Paiements ─────────────────────────────────────────────────────────────────
@login_required
@paiement_required
def paiement_list(request):
    annee_pk = request.GET.get('annee')
    q = request.GET.get('q', '')
    paiements = Paiement.objects.select_related('inscription__eleve', 'inscription__annee_scolaire')
    if annee_pk:
        paiements = paiements.filter(inscription__annee_scolaire__pk=annee_pk)
    if q:
        paiements = paiements.filter(
            Q(inscription__eleve__nom__icontains=q) |
            Q(inscription__eleve__prenom__icontains=q) |
            Q(reference__icontains=q)
        )
    total = paiements.aggregate(total=Sum('montant'))['total'] or 0
    annees = AnneeScolaire.objects.all()
    return render(request, 'attendance_payments/paiement_list.html', {
        'paiements': paiements, 'total': total,
        'annees': annees, 'annee_active': annee_pk, 'q': q
    })


@login_required
@paiement_required
def paiement_create(request):
    form = PaiementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            p = form.save(commit=False)
            p.recu_par = p.recu_par or request.user.get_full_name() or request.user.username
            p.full_clean()
            p.save()
            messages.success(request, f'Paiement {p.reference} enregistré.')
            return redirect('attendance_payments:paiement_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'attendance_payments/paiement_form.html', {'form': form, 'title': 'Nouveau paiement'})


@login_required
@paiement_required
def paiement_edit(request, pk):
    obj = get_object_or_404(Paiement, pk=pk)
    form = PaiementForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        try:
            p = form.save(commit=False)
            p.full_clean()
            p.save()
            messages.success(request, 'Paiement mis à jour.')
            return redirect('attendance_payments:paiement_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'attendance_payments/paiement_form.html', {
        'form': form, 'title': 'Modifier le paiement', 'object': obj
    })


@login_required
@paiement_required
def paiement_delete(request, pk):
    obj = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Paiement supprimé.')
        return redirect('attendance_payments:paiement_list')
    return render(request, 'attendance_payments/confirm_delete.html', {
        'object': obj, 'title': 'Supprimer le paiement'
    })


@login_required
@paiement_required
def suivi_paiements(request):
    """Vue de suivi des paiements par inscription — soldes restants."""
    annee_pk = request.GET.get('annee')
    inscriptions = Inscription.objects.select_related('eleve', 'classe', 'annee_scolaire').filter(statut='actif')
    if annee_pk:
        inscriptions = inscriptions.filter(annee_scolaire__pk=annee_pk)
    annees = AnneeScolaire.objects.all()
    return render(request, 'attendance_payments/suivi_paiements.html', {
        'inscriptions': inscriptions, 'annees': annees, 'annee_active': annee_pk
    })


# ── Actions & Services de Notification / Communication ─────────────────────────
@login_required
@paiement_required
def relance_paiement_view(request, pk):
    """Déclenche l'envoi du gabarit de relance pour une inscription donnée."""
    inscription = get_object_or_404(Inscription, pk=pk)
    success, msg = envoyer_relance_paiement(inscription)
    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)
    return redirect('attendance_payments:suivi_paiements')


# ── Points de terminaison API JSON ─────────────────────────────────────────────
@login_required
@paiement_required
@require_http_methods(["POST"])
def api_envoyer_relance(request, inscription_id):
    """
    API JSON permettant d'automatiser l'envoi d'une relance de frais de scolarité.
    Corps attendu (optionnel) : {"date_echeance": "15 du mois"}
    """
    try:
        inscription = Inscription.objects.get(pk=inscription_id)
    except Inscription.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Inscription introuvable.'}, status=404)

    date_echeance = "Fin du mois en cours"
    if request.body:
        try:
            data = json.loads(request.body)
            date_echeance = data.get('date_echeance', date_echeance)
        except json.JSONDecodeError:
            pass

    success, message = envoyer_relance_paiement(inscription, date_echeance=date_echeance)
    return JsonResponse({
        'status': 'success' if success else 'warning',
        'message': message,
        'solde_restant': float(inscription.solde_restant)
    })


@login_required
@direction_required
@require_http_methods(["POST"])
def api_envoyer_convocation(request, inscription_id):
    """
    API JSON permettant de convoquer le tuteur d'un élève.
    Corps attendu : {"date_rdv": "YYYY-MM-DD", "heure_rdv": "10:00", "motif": "..."}
    """
    try:
        inscription = Inscription.objects.get(pk=inscription_id)
    except Inscription.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Inscription introuvable.'}, status=404)

    try:
        data = json.loads(request.body)
        date_rdv = data.get('date_rdv', 'Prochainement')
        heure_rdv = data.get('heure_rdv', '09h00')
        motif = data.get('motif', 'Entretien de suivi')
        interlocuteurs = data.get('interlocuteurs', 'La Direction')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Données JSON invalides.'}, status=400)

    success, message = envoyer_convocation_parent(
        inscription, date_rdv=date_rdv, heure_rdv=heure_rdv,
        motif=motif, interlocuteurs=interlocuteurs
    )
    return JsonResponse({'status': 'success' if success else 'warning', 'message': message})
