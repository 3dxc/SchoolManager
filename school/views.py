from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Etablissement, AnneeScolaire, Classe, Matiere, Campus, SignalementProbleme
from .forms import EtablissementForm, AnneeScolaireForm, ClasseForm, MatiereForm, SignalementForm
from accounts.decorators import direction_required


# ── Établissement ─────────────────────────────────────────────────────────────
@login_required
@direction_required
def etablissement_list(request):
    etablissements = Etablissement.objects.all()
    return render(request, 'school/etablissement_list.html', {'etablissements': etablissements})


@login_required
@direction_required
def etablissement_create(request):
    form = EtablissementForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Établissement créé avec succès.')
        return redirect('school:etablissement_list')
    return render(request, 'school/etablissement_form.html', {'form': form, 'title': 'Ajouter un établissement'})


@login_required
@direction_required
def etablissement_edit(request, pk):
    obj = get_object_or_404(Etablissement, pk=pk)
    form = EtablissementForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Établissement mis à jour.')
        return redirect('school:etablissement_list')
    return render(request, 'school/etablissement_form.html', {'form': form, 'title': 'Modifier l\'établissement', 'object': obj})


@login_required
@direction_required
def etablissement_delete(request, pk):
    obj = get_object_or_404(Etablissement, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Établissement supprimé.')
        return redirect('school:etablissement_list')
    return render(request, 'school/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'établissement'})


# ── Année scolaire ────────────────────────────────────────────────────────────
@login_required
def annee_list(request):
    annees = AnneeScolaire.objects.select_related('etablissement').all()
    return render(request, 'school/annee_list.html', {'annees': annees})


@login_required
@direction_required
def annee_create(request):
    form = AnneeScolaireForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            form.full_clean()
            form.save()
            messages.success(request, 'Année scolaire créée.')
            return redirect('school:annee_list')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'school/annee_form.html', {'form': form, 'title': 'Nouvelle année scolaire'})


@login_required
@direction_required
def annee_edit(request, pk):
    obj = get_object_or_404(AnneeScolaire, pk=pk)
    form = AnneeScolaireForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Année scolaire mise à jour.')
        return redirect('school:annee_list')
    return render(request, 'school/annee_form.html', {'form': form, 'title': 'Modifier l\'année scolaire', 'object': obj})


@login_required
@direction_required
def annee_delete(request, pk):
    obj = get_object_or_404(AnneeScolaire, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Année scolaire supprimée.')
        return redirect('school:annee_list')
    return render(request, 'school/confirm_delete.html', {'object': obj, 'title': 'Supprimer l\'année scolaire'})


# ── Classe ────────────────────────────────────────────────────────────────────
@login_required
def classe_list(request):
    annee_pk = request.GET.get('annee')
    classes = Classe.objects.select_related('annee_scolaire__etablissement')
    if annee_pk:
        classes = classes.filter(annee_scolaire__pk=annee_pk)
    annees = AnneeScolaire.objects.all()
    return render(request, 'school/classe_list.html', {'classes': classes, 'annees': annees, 'annee_active': annee_pk})


@login_required
@direction_required
def classe_create(request):
    form = ClasseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Classe créée avec succès.')
        return redirect('school:classe_list')
    return render(request, 'school/classe_form.html', {'form': form, 'title': 'Nouvelle classe'})


@login_required
@direction_required
def classe_edit(request, pk):
    obj = get_object_or_404(Classe, pk=pk)
    form = ClasseForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Classe mise à jour.')
        return redirect('school:classe_list')
    return render(request, 'school/classe_form.html', {'form': form, 'title': 'Modifier la classe', 'object': obj})


@login_required
@direction_required
def classe_delete(request, pk):
    obj = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Classe supprimée.')
        return redirect('school:classe_list')
    return render(request, 'school/confirm_delete.html', {'object': obj, 'title': 'Supprimer la classe'})


# ── Matière ───────────────────────────────────────────────────────────────────
@login_required
def matiere_list(request):
    matieres = Matiere.objects.all()
    q = request.GET.get('q', '')
    if q:
        matieres = matieres.filter(nom__icontains=q)
    return render(request, 'school/matiere_list.html', {'matieres': matieres, 'q': q})


@login_required
@direction_required
def matiere_create(request):
    form = MatiereForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Matière créée.')
        return redirect('school:matiere_list')
    return render(request, 'school/matiere_form.html', {'form': form, 'title': 'Nouvelle matière'})


@login_required
@direction_required
def matiere_edit(request, pk):
    obj = get_object_or_404(Matiere, pk=pk)
    form = MatiereForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Matière mise à jour.')
        return redirect('school:matiere_list')
    return render(request, 'school/matiere_form.html', {'form': form, 'title': 'Modifier la matière', 'object': obj})


@login_required
@direction_required
def matiere_delete(request, pk):
    obj = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Matière supprimée.')
        return redirect('school:matiere_list')
    return render(request, 'school/confirm_delete.html', {'object': obj, 'title': 'Supprimer la matière'})


# ── Signalement de Problème ───────────────────────────────────────────────────
def signalement_create(request):
    """
    Enregistre un signalement ou une demande d'assistance (problème d'accès,
    carte, locaux, inscription, etc.) et le rend disponible pour l'administration.
    """
    if request.method == 'POST':
        form = SignalementForm(request.POST)
        if form.is_valid():
            signalement = form.save(commit=False)
            if request.user.is_authenticated:
                if not signalement.nom and (request.user.first_name or request.user.last_name):
                    signalement.nom = request.user.get_full_name()
                elif not signalement.nom:
                    signalement.nom = request.user.username
                if not signalement.email and request.user.email:
                    signalement.email = request.user.email
            signalement.save()
            messages.success(
                request,
                f"Votre signalement #{signalement.id} ({signalement.get_type_probleme_display()}) "
                f"a bien été transmis à l'administration. Merci de votre contribution !"
            )
        else:
            messages.error(
                request,
                "Impossible d'enregistrer le signalement. Veuillez vérifier les champs obligatoires."
            )
    return redirect('dashboard')

