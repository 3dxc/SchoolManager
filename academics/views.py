from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Enseignant, Affectation, Note
from .forms import EnseignantForm, AffectationForm, NoteForm
from students.models import Inscription
from school.models import AnneeScolaire, Matiere
from accounts.decorators import direction_required, enseignant_required


# ── Enseignants ───────────────────────────────────────────────────────────────
@login_required
@direction_required
def enseignant_list(request):
    q = request.GET.get('q', '')
    enseignants = Enseignant.objects.all()
    if q:
        enseignants = enseignants.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(specialite__icontains=q))
    return render(request, 'academics/enseignant_list.html', {'enseignants': enseignants, 'q': q})


@login_required
@direction_required
def enseignant_create(request):
    form = EnseignantForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Enseignant créé.')
        return redirect('academics:enseignant_list')
    return render(request, 'academics/enseignant_form.html', {'form': form, 'title': 'Nouvel enseignant'})


@login_required
@direction_required
def enseignant_edit(request, pk):
    obj = get_object_or_404(Enseignant, pk=pk)
    form = EnseignantForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Enseignant mis à jour.')
        return redirect('academics:enseignant_list')
    return render(request, 'academics/enseignant_form.html', {'form': form, 'title': 'Modifier l\'enseignant', 'object': obj})


@login_required
@direction_required
def enseignant_delete(request, pk):
    obj = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Enseignant supprimé.')
        return redirect('academics:enseignant_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'enseignant'})


# ── Affectations ──────────────────────────────────────────────────────────────
@login_required
@direction_required
def affectation_list(request):
    annee_pk = request.GET.get('annee')
    affectations = Affectation.objects.select_related('enseignant', 'matiere', 'classe', 'annee_scolaire')
    if annee_pk:
        affectations = affectations.filter(annee_scolaire__pk=annee_pk)
    annees = AnneeScolaire.objects.all()
    return render(request, 'academics/affectation_list.html', {
        'affectations': affectations, 'annees': annees, 'annee_active': annee_pk
    })


@login_required
@direction_required
def affectation_create(request):
    form = AffectationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Affectation créée.')
        return redirect('academics:affectation_list')
    return render(request, 'academics/affectation_form.html', {'form': form, 'title': 'Nouvelle affectation'})


@login_required
@direction_required
def affectation_delete(request, pk):
    obj = get_object_or_404(Affectation, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Affectation supprimée.')
        return redirect('academics:affectation_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'affectation'})


# ── Notes ─────────────────────────────────────────────────────────────────────
@login_required
@enseignant_required
def note_list(request):
    inscription_pk = request.GET.get('inscription')
    periode = request.GET.get('periode', '')
    notes = Note.objects.select_related('inscription__eleve', 'matiere')
    # Un enseignant ne voit que les notes de ses classes
    if request.user.role == 'enseignant' and hasattr(request.user, 'enseignant_profil'):
        enseignant = request.user.enseignant_profil
        affectations = Affectation.objects.filter(enseignant=enseignant)
        classes = affectations.values_list('classe', flat=True)
        annees = affectations.values_list('annee_scolaire', flat=True)
        notes = notes.filter(inscription__classe__in=classes, inscription__annee_scolaire__in=annees)
    if inscription_pk:
        notes = notes.filter(inscription__pk=inscription_pk)
    if periode:
        notes = notes.filter(periode=periode)
    periodes = Note.PERIODE_CHOICES
    return render(request, 'academics/note_list.html', {
        'notes': notes, 'periodes': periodes, 'periode_active': periode
    })


@login_required
@enseignant_required
def note_create(request):
    form = NoteForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            note = form.save(commit=False)
            note.saisie_par = request.user
            note.full_clean()
            note.save()
            messages.success(request, 'Note enregistrée.')
            return redirect('academics:note_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'academics/note_form.html', {'form': form, 'title': 'Saisir une note'})


@login_required
@enseignant_required
def note_edit(request, pk):
    obj = get_object_or_404(Note, pk=pk)
    # Vérification d'accès enseignant
    if request.user.role == 'enseignant' and hasattr(request.user, 'enseignant_profil'):
        enseignant = request.user.enseignant_profil
        if not Affectation.objects.filter(
            enseignant=enseignant,
            matiere=obj.matiere,
            classe=obj.inscription.classe,
            annee_scolaire=obj.inscription.annee_scolaire
        ).exists():
            messages.error(request, "Vous n'avez pas accès à cette note.")
            return redirect('academics:note_list')
    form = NoteForm(request.POST or None, instance=obj, user=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            note = form.save(commit=False)
            note.full_clean()
            note.save()
            messages.success(request, 'Note mise à jour.')
            return redirect('academics:note_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'academics/note_form.html', {'form': form, 'title': 'Modifier la note', 'object': obj})


@login_required
@enseignant_required
def note_delete(request, pk):
    obj = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Note supprimée.')
        return redirect('academics:note_list')
    return render(request, 'academics/confirm_delete.html', {'object': obj, 'title': 'Supprimer la note'})


# ── Bulletin ──────────────────────────────────────────────────────────────────
@login_required
@enseignant_required
def bulletin(request, inscription_pk):
    inscription = get_object_or_404(
        Inscription.objects.select_related('eleve', 'classe', 'annee_scolaire'),
        pk=inscription_pk
    )
    periode = request.GET.get('periode', '')
    periodes = Note.PERIODE_CHOICES

    # Récupérer les affectations (matières) de la classe
    affectations = Affectation.objects.filter(
        classe=inscription.classe,
        annee_scolaire=inscription.annee_scolaire
    ).select_related('matiere', 'enseignant')

    # Récupérer les notes de cette inscription
    notes_qs = Note.objects.filter(inscription=inscription)
    if periode:
        notes_qs = notes_qs.filter(periode=periode)

    # Construire le tableau du bulletin
    lignes_bulletin = []
    total_points = 0
    total_coeff = 0
    for aff in affectations:
        notes_matiere = notes_qs.filter(matiere=aff.matiere)
        moyenne_matiere = notes_matiere.aggregate(moy=Avg('valeur'))['moy']
        coeff = aff.matiere.coefficient
        if moyenne_matiere is not None:
            total_points += float(moyenne_matiere) * coeff
            total_coeff += coeff
        lignes_bulletin.append({
            'matiere': aff.matiere,
            'enseignant': aff.enseignant,
            'notes': notes_matiere,
            'moyenne': round(moyenne_matiere, 2) if moyenne_matiere is not None else None,
            'coefficient': coeff,
        })

    moyenne_generale = round(total_points / total_coeff, 2) if total_coeff > 0 else None

    # Absences
    from attendance_payments.models import Absence
    absences = Absence.objects.filter(inscription=inscription)
    nb_absences = absences.count()

    return render(request, 'academics/bulletin.html', {
        'inscription': inscription,
        'lignes_bulletin': lignes_bulletin,
        'moyenne_generale': moyenne_generale,
        'nb_absences': nb_absences,
        'periode': periode,
        'periodes': periodes,
    })


@login_required
@enseignant_required
def notifier_bulletin(request, inscription_pk):
    """Envoie par email une notification de mise à disposition du bulletin au tuteur de l'élève."""
    inscription = get_object_or_404(Inscription, pk=inscription_pk)
    periode = request.GET.get('periode', 'Trimestre')

    from attendance_payments.models import Absence
    from attendance_payments.services import envoyer_notification_bulletin

    # Calcul rapide de la moyenne générale
    notes = Note.objects.filter(inscription=inscription)
    if periode:
        notes = notes.filter(periode=periode)
    moy = notes.aggregate(Avg('valeur'))['valeur__avg']
    moyenne_str = f"{round(moy, 2)}" if moy is not None else "En cours"
    nb_absences = Absence.objects.filter(inscription=inscription).count()

    dict_periodes = dict(Note.PERIODE_CHOICES)
    periode_libelle = dict_periodes.get(periode, periode)

    success, message = envoyer_notification_bulletin(
        inscription=inscription,
        periode_libelle=periode_libelle,
        moyenne_generale=moyenne_str,
        nb_absences=nb_absences
    )

    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)

    return redirect('academics:bulletin', inscription_pk=inscription.pk)
