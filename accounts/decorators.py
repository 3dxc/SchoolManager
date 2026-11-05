from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    """Décorateur qui vérifie que l'utilisateur possède l'un des rôles donnés."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('/')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required('admin')(view_func)


def direction_required(view_func):
    return role_required('admin', 'direction')(view_func)


def enseignant_required(view_func):
    return role_required('admin', 'direction', 'enseignant')(view_func)


def paiement_required(view_func):
    return role_required('admin', 'direction', 'paiement')(view_func)
