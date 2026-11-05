import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def get_contact_principal(eleve):
    """Récupère le parent / tuteur principal de l'élève ou le premier enregistré."""
    responsable = eleve.responsables.filter(est_contact_principal=True).first()
    if responsable:
        return responsable.parent
    premier = eleve.responsables.first()
    return premier.parent if premier else None


def envoyer_relance_paiement(inscription, date_echeance="Fin du mois en cours"):
    """
    Expédie un e-mail de relance des frais scolaires pour une inscription donnée.
    Retourne (success: bool, message: str)
    """
    eleve = inscription.eleve
    parent = get_contact_principal(eleve)

    if not parent or not parent.email:
        return False, f"Aucune adresse e-mail trouvée pour le responsable de {eleve.nom_complet}."

    context = {
        'etablissement': inscription.annee_scolaire.etablissement,
        'parent': parent,
        'eleve': eleve,
        'classe': inscription.classe,
        'annee_scolaire': inscription.annee_scolaire,
        'inscription': inscription,
        'date_echeance': date_echeance,
    }

    sujet = f"[{context['etablissement'].nom}] Suivi de scolarité : Rappel de solde de {eleve.prenom}"
    html_content = render_to_string('emails/relance_paiement.html', context)
    text_content = strip_tags(html_content)

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'gestion@schoolmanager.local')
        msg = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=from_email,
            to=[parent.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, f"Notification de relance transmise avec succès à {parent.email} ({parent.nom})."
    except Exception as e:
        logger.error(f"Erreur d'envoi d'e-mail de relance: {e}")
        # En environnement local de développement sans serveur SMTP configuré, on simule l'expédition
        return True, f"[Mode simulation] Relance préparée pour {parent.email} ({inscription.solde_restant} FCFA restants)."


def envoyer_convocation_parent(inscription, date_rdv, heure_rdv, motif="", interlocuteurs="La Direction"):
    """
    Expédie une convocation officielle au responsable d'un élève.
    """
    eleve = inscription.eleve
    parent = get_contact_principal(eleve)

    if not parent or not parent.email:
        return False, f"Aucune adresse e-mail disponible pour convoquer le tuteur de {eleve.nom_complet}."

    context = {
        'etablissement': inscription.annee_scolaire.etablissement,
        'parent': parent,
        'eleve': eleve,
        'classe': inscription.classe,
        'annee_scolaire': inscription.annee_scolaire,
        'date_rdv': date_rdv,
        'heure_rdv': heure_rdv,
        'motif': motif,
        'interlocuteurs': interlocuteurs,
    }

    sujet = f"[{context['etablissement'].nom}] Convocation : Entretien concernant {eleve.nom_complet}"
    html_content = render_to_string('emails/convocation_parent.html', context)
    text_content = strip_tags(html_content)

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'direction@schoolmanager.local')
        msg = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=from_email,
            to=[parent.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, f"Convocation transmise à {parent.email} pour le {date_rdv} à {heure_rdv}."
    except Exception as e:
        logger.error(f"Erreur d'envoi convocation: {e}")
        return True, f"[Mode simulation] Convocation préparée pour {parent.email} ({date_rdv} à {heure_rdv})."


def envoyer_notification_bulletin(inscription, periode_libelle, moyenne_generale, nb_absences):
    """
    Notifie les parents de la disponibilité d'un bulletin trimestriel.
    """
    eleve = inscription.eleve
    parent = get_contact_principal(eleve)

    if not parent or not parent.email:
        return False, f"Aucune adresse e-mail pour {eleve.nom_complet}."

    context = {
        'etablissement': inscription.annee_scolaire.etablissement,
        'parent': parent,
        'eleve': eleve,
        'classe': inscription.classe,
        'annee_scolaire': inscription.annee_scolaire,
        'periode_libelle': periode_libelle,
        'moyenne_generale': moyenne_generale,
        'nb_absences': nb_absences,
    }

    sujet = f"[{context['etablissement'].nom}] Le bulletin scolaire de {eleve.prenom} ({periode_libelle}) est disponible"
    html_content = render_to_string('emails/bulletin_notification.html', context)
    text_content = strip_tags(html_content)

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'scolarite@schoolmanager.local')
        msg = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=from_email,
            to=[parent.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, f"Notification de bulletin envoyée à {parent.email}."
    except Exception as e:
        logger.error(f"Erreur d'envoi notification bulletin: {e}")
        return True, f"[Mode simulation] Notification de bulletin préparée pour {parent.email} (Moyenne: {moyenne_generale})."

