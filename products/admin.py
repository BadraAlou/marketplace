from django.contrib import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import format_html
from .models import Category, SubCategory, Product, UserProfile, Suggestion, ContactMessage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_seller', 'is_seller_validated', 'subscription_plan', 'is_subscription_active',
                    'current_product_count', 'product_limit_display', 'created_at']
    list_filter = ['is_seller', 'is_seller_validated', 'subscription_plan', 'is_subscription_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    actions = ['validate_sellers', 'activate_subscription', 'deactivate_subscription', 'upgrade_to_medium',
               'upgrade_to_large', 'downgrade_to_small']

    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'is_seller', 'is_seller_validated')
        }),
        ('Abonnement', {
            'fields': (
            'subscription_plan', 'subscription_start_date', 'subscription_end_date', 'is_subscription_active'),
            'description': 'Vous pouvez modifier le plan d\'abonnement du vendeur ici. Les limites de produits seront automatiquement mises à jour.'
        }),
        ('Statistiques', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']

    def current_product_count(self, obj):
        count = obj.current_product_count
        limit = obj.product_limit

        if limit is None:
            color = 'green'
            text = f"{count} produits (Illimité)"
        elif count >= limit:
            color = 'red'
            text = f"{count}/{limit} produits (LIMITE ATTEINTE)"
        elif count >= limit * 0.8:
            color = 'orange'
            text = f"{count}/{limit} produits (Proche de la limite)"
        else:
            color = 'green'
            text = f"{count}/{limit} produits"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    current_product_count.short_description = "Produits actuels"

    def product_limit_display(self, obj):
        limit = obj.product_limit
        if limit is None:
            return format_html('<span style="color: green; font-weight: bold;">♾️ Illimité</span>')
        return format_html('<span style="color: blue; font-weight: bold;">{} produits max</span>', limit)

    product_limit_display.short_description = "Limite"

    def validate_sellers(self, request, queryset):
        """Action pour valider les vendeurs sélectionnés"""
        validated_count = 0

        for user_profile in queryset.filter(is_seller=True, is_seller_validated=False):
            # Marquer comme validé et activer l'abonnement
            user_profile.is_seller_validated = True
            user_profile.is_subscription_active = True
            if not user_profile.subscription_start_date:
                from django.utils import timezone
                user_profile.subscription_start_date = timezone.now().date()
            user_profile.save()

            # Envoyer l'email de validation
            self.send_validation_email(user_profile)
            validated_count += 1

        if validated_count > 0:
            self.message_user(
                request,
                f"{validated_count} vendeur(s) validé(s) avec succès. Les abonnements ont été activés et les emails envoyés."
            )
        else:
            self.message_user(request, "Aucun vendeur à valider dans la sélection.")

    validate_sellers.short_description = "✅ Valider les vendeurs et activer l'abonnement"

    def activate_subscription(self, request, queryset):
        updated = queryset.update(is_subscription_active=True)
        self.message_user(request, f'{updated} abonnement(s) activé(s).')

    activate_subscription.short_description = "🟢 Activer l'abonnement"

    def deactivate_subscription(self, request, queryset):
        updated = queryset.update(is_subscription_active=False)
        self.message_user(request, f'{updated} abonnement(s) désactivé(s).')

    deactivate_subscription.short_description = "🔴 Désactiver l'abonnement"

    def upgrade_to_medium(self, request, queryset):
        updated = queryset.update(subscription_plan='medium')
        self.message_user(request, f'{updated} vendeur(s) mis à niveau vers Medium (20 produits).')

    upgrade_to_medium.short_description = "⬆️ Passer au plan Medium"

    def upgrade_to_large(self, request, queryset):
        updated = queryset.update(subscription_plan='large')
        self.message_user(request, f'{updated} vendeur(s) mis à niveau vers Large (illimité).')

    upgrade_to_large.short_description = "⬆️⬆️ Passer au plan Large"

    def downgrade_to_small(self, request, queryset):
        updated = queryset.update(subscription_plan='small')
        self.message_user(request, f'{updated} vendeur(s) rétrogradé(s) vers Small (7 produits).')

    downgrade_to_small.short_description = "⬇️ Rétrograder au plan Small"

    def send_validation_email(self, user_profile):
        """Envoie l'email de validation au vendeur"""
        try:
            subject = 'Félicitations ! Votre compte vendeur a été validé'

            # Contexte pour le template
            context = {
                'user': user_profile.user,
                'site_name': 'MonMarché',
                'subscription_plan': user_profile.get_subscription_plan_display(),
                'product_limit': user_profile.product_limit if user_profile.product_limit else "Illimité",
            }

            # Rendu du template HTML
            html_message = render_to_string('emails/seller_validation.html', context)

            # Message texte simple
            plain_message = f"""
Bonjour {user_profile.user.username},

Excellente nouvelle ! Votre compte vendeur sur MonMarché a été validé par notre équipe.

Plan d'abonnement : {user_profile.get_subscription_plan_display()}
Limite de produits : {user_profile.product_limit if user_profile.product_limit else "Illimité"}

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

    def save_model(self, request, obj, form, change):
        """Surcharge pour gérer les changements d'abonnement"""
        if change:
            try:
                # Récupérer l'ancienne valeur
                old_obj = UserProfile.objects.get(pk=obj.pk)

                # Si le vendeur vient d'être validé
                if obj.is_seller and obj.is_seller_validated and not old_obj.is_seller_validated:
                    # Activer automatiquement l'abonnement
                    obj.is_subscription_active = True
                    if not obj.subscription_start_date:
                        from django.utils import timezone
                        obj.subscription_start_date = timezone.now().date()
                    super().save_model(request, obj, form, change)
                    self.send_validation_email(obj)
                    return

                # Si le plan d'abonnement a changé
                if old_obj.subscription_plan != obj.subscription_plan:
                    self.message_user(
                        request,
                        f"Plan d'abonnement de {obj.user.username} changé de {old_obj.get_subscription_plan_display()} vers {obj.get_subscription_plan_display()}. "
                        f"Nouvelle limite: {obj.product_limit if obj.product_limit else 'Illimité'} produits."
                    )

                    # Vérifier si le vendeur dépasse maintenant sa limite
                    if obj.product_limit and obj.current_product_count > obj.product_limit:
                        self.message_user(
                            request,
                            f"⚠️ ATTENTION: {obj.user.username} a {obj.current_product_count} produits mais sa nouvelle limite est de {obj.product_limit}. "
                            f"Le vendeur ne pourra plus ajouter de produits jusqu'à ce qu'il en supprime.",
                            level='WARNING'
                        )

            except UserProfile.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category__name', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'seller', 'seller_plan_display', 'seller_product_count',
                    'created_at']
    list_filter = ['category', 'subcategory', 'created_at', 'seller__userprofile__subscription_plan']
    search_fields = ['name', 'description']
    raw_id_fields = ['seller']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 20

    def seller_plan_display(self, obj):
        try:
            plan = obj.seller.userprofile.get_subscription_plan_display()
            colors = {
                'Small': 'green',
                'Medium': 'blue',
                'Large': 'purple'
            }
            plan_name = plan.split(' - ')[0]
            color = colors.get(plan_name, 'gray')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, plan_name
            )
        except:
            return "Non défini"

    seller_plan_display.short_description = "Plan vendeur"

    def seller_product_count(self, obj):
        try:
            profile = obj.seller.userprofile
            count = profile.current_product_count
            limit = profile.product_limit

            if limit is None:
                return format_html('<span style="color: green;">{}/∞</span>', count)
            elif count >= limit:
                return format_html('<span style="color: red; font-weight: bold;">{}/{} (MAX)</span>', count, limit)
            else:
                return format_html('<span style="color: blue;">{}/{}</span>', count, limit)
        except:
            return "N/A"

    seller_product_count.short_description = "Produits vendeur"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(seller=request.user)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marqué(s) comme lu(s).')

    mark_as_read.short_description = "Marquer comme lu"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marqué(s) comme non lu(s).')

    mark_as_unread.short_description = "Marquer comme non lu"


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']