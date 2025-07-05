from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserProfile


@receiver(post_save, sender=UserProfile)
def send_seller_validation_email(sender, instance, created, **kwargs):
    """
    Envoie un email au vendeur quand son compte est validé
    """
    # Vérifier si c'est une mise à jour (pas une création) et si le vendeur vient d'être validé
    if not created and instance.is_seller and instance.is_seller_validated:
        # Vérifier si le statut de validation a changé
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Récupérer l'ancienne valeur depuis la base de données
            try:
                old_instance = UserProfile.objects.get(pk=instance.pk)
                # Si l'ancien statut était False et le nouveau est True
                if hasattr(old_instance,
                           'is_seller_validated') and not old_instance.is_seller_validated and instance.is_seller_validated:
                    send_validation_email(instance)
            except UserProfile.DoesNotExist:
                pass


def send_validation_email(user_profile):
    """
    Envoie l'email de validation au vendeur
    """
    try:
        subject = 'Félicitations ! Votre compte vendeur a été validé'

        # Contexte pour le template
        context = {
            'user': user_profile.user,
            'site_name': 'MonMarché',
        }

        # Rendu du template HTML
        html_message = render_to_string('emails/seller_validation.html', context)

        # Message texte simple
        plain_message = f"""
Bonjour {user_profile.user.username},

Excellente nouvelle ! Votre compte vendeur sur MonMarché a été validé par notre équipe.

Vous pouvez maintenant :
✅ Ajouter vos produits
✅ Gérer votre catalogue
✅ Commencer à vendre

Connectez-vous à votre tableau de bord pour commencer à publier vos articles.

Merci de faire confiance à MonMarché !

L'équipe MonMarché
        """

        # Envoi de l'email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_profile.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"Email de validation envoyé à {user_profile.user.email}")

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")