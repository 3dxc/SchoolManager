from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Eleve, Parent, ResponsableEleve, Inscription
from .forms import EleveForm, ParentForm, ResponsableEleveForm, InscriptionForm
from accounts.decorators import direction_required


# ── Élèves ────────────────────────────────────────────────────────────────────
@login_required
def eleve_list(request):
    q = request.GET.get('q', '')
    eleves = Eleve.objects.all()
    if q:
        eleves = eleves.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(matricule__icontains=q))
    return render(request, 'students/eleve_list.html', {'eleves': eleves, 'q': q})


@login_required
def eleve_detail(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    inscriptions = eleve.inscriptions.select_related('classe', 'annee_scolaire').all()
    responsables = eleve.responsables.select_related('parent').all()
    return render(request, 'students/eleve_detail.html', {
        'eleve': eleve,
        'inscriptions': inscriptions,
        'responsables': responsables,
    })


@login_required
@direction_required
def eleve_create(request):
    form = EleveForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Élève créé avec succès.')
        return redirect('students:eleve_list')
    return render(request, 'students/eleve_form.html', {'form': form, 'title': 'Nouvel élève'})


@login_required
@direction_required
def eleve_edit(request, pk):
    obj = get_object_or_404(Eleve, pk=pk)
    form = EleveForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Élève mis à jour.')
        return redirect('students:eleve_detail', pk=pk)
    return render(request, 'students/eleve_form.html', {'form': form, 'title': 'Modifier l\'élève', 'object': obj})


@login_required
@direction_required
def eleve_delete(request, pk):
    obj = get_object_or_404(Eleve, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Élève supprimé.')
        return redirect('students:eleve_list')
    return render(request, 'students/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'élève'})


# ── Parents ───────────────────────────────────────────────────────────────────
@login_required
def parent_list(request):
    q = request.GET.get('q', '')
    parents = Parent.objects.all()
    if q:
        parents = parents.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q))
    return render(request, 'students/parent_list.html', {'parents': parents, 'q': q})


@login_required
@direction_required
def parent_create(request):
    form = ParentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parent créé.')
        return redirect('students:parent_list')
    return render(request, 'students/parent_form.html', {'form': form, 'title': 'Nouveau parent / tuteur'})


@login_required
@direction_required
def parent_edit(request, pk):
    obj = get_object_or_404(Parent, pk=pk)
    form = ParentForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parent mis à jour.')
        return redirect('students:parent_list')
    return render(request, 'students/parent_form.html', {'form': form, 'title': 'Modifier le parent', 'object': obj})


@login_required
@direction_required
def parent_delete(request, pk):
    obj = get_object_or_404(Parent, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Parent supprimé.')
        return redirect('students:parent_list')
    return render(request, 'students/confirm_delete.html', {'object': obj, 'title': 'Supprimer le parent'})


# ── Inscriptions ──────────────────────────────────────────────────────────────
@login_required
def inscription_list(request):
    annee_pk = request.GET.get('annee')
    statut = request.GET.get('statut', '')
    q = request.GET.get('q', '')
    inscriptions = Inscription.objects.select_related('eleve', 'classe', 'annee_scolaire')
    if annee_pk:
        inscriptions = inscriptions.filter(annee_scolaire__pk=annee_pk)
    if statut:
        inscriptions = inscriptions.filter(statut=statut)
    if q:
        inscriptions = inscriptions.filter(
            Q(eleve__nom__icontains=q) | Q(eleve__prenom__icontains=q) | Q(eleve__matricule__icontains=q)
        )
    from school.models import AnneeScolaire
    annees = AnneeScolaire.objects.all()
    return render(request, 'students/inscription_list.html', {
        'inscriptions': inscriptions,
        'annees': annees,
        'statuts': Inscription.STATUT_CHOICES,
        'annee_active': annee_pk,
        'statut_actif': statut,
        'q': q,
    })


@login_required
@direction_required
def inscription_create(request):
    form = InscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            inscription = form.save(commit=False)
            inscription.full_clean()
            inscription.save()
            messages.success(request, 'Inscription enregistrée.')
            return redirect('students:inscription_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'students/inscription_form.html', {'form': form, 'title': 'Nouvelle inscription'})


@login_required
@direction_required
def inscription_edit(request, pk):
    obj = get_object_or_404(Inscription, pk=pk)
    form = InscriptionForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        try:
            inscription = form.save(commit=False)
            inscription.full_clean()
            inscription.save()
            messages.success(request, 'Inscription mise à jour.')
            return redirect('students:inscription_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'students/inscription_form.html', {
        'form': form, 'title': 'Modifier l\'inscription', 'object': obj
    })


@login_required
@direction_required
def inscription_delete(request, pk):
    obj = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Inscription supprimée.')
        return redirect('students:inscription_list')
    return render(request, 'students/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'inscription'})
