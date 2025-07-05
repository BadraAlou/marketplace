from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('small', 'Small - 7 produits'),
        ('medium', 'Medium - 20 produits'),
        ('large', 'Large - Illimité'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
    is_seller_validated = models.BooleanField(default=False)
    subscription_plan = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='small',
                                         verbose_name='Plan d\'abonnement')
    subscription_start_date = models.DateField(null=True, blank=True, verbose_name='Date de début d\'abonnement')
    subscription_end_date = models.DateField(null=True, blank=True, verbose_name='Date de fin d\'abonnement')
    is_subscription_active = models.BooleanField(default=False, verbose_name='Abonnement actif')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = 'Vendeur validé' if self.is_seller_validated else 'Vendeur en attente' if self.is_seller else 'Acheteur'
        if self.is_seller and self.is_seller_validated:
            status += f' - {self.get_subscription_plan_display()}'
        return f"{self.user.username} ({status})"

    @property
    def product_limit(self):
        """Retourne la limite de produits selon le plan d'abonnement"""
        limits = {
            'small': 7,
            'medium': 20,
            'large': None  # Illimité
        }
        return limits.get(self.subscription_plan, 7)

    @property
    def current_product_count(self):
        """Retourne le nombre actuel de produits du vendeur"""
        return self.user.product_set.count()

    @property
    def can_add_product(self):
        """Vérifie si le vendeur peut ajouter un nouveau produit"""
        if not self.is_seller or not self.is_seller_validated or not self.is_subscription_active:
            return False

        limit = self.product_limit
        if limit is None:  # Plan Large (illimité)
            return True

        return self.current_product_count < limit

    @property
    def remaining_products(self):
        """Retourne le nombre de produits restants"""
        limit = self.product_limit
        if limit is None:
            return "Illimité"

        remaining = limit - self.current_product_count
        return max(0, remaining)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône Lucide (ex: smartphone, shirt, watch)")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'subcategories'
        unique_together = ['category', 'slug']
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def seller_email(self):
        return self.seller.email


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, help_text="Résumé de l'article")
    image = models.URLField(help_text="URL de l'image depuis Unsplash")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message de {self.name} - {self.subject}"


class Suggestion(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suggestion de {self.name} - {self.created_at.strftime('%d/%m/%Y')}"