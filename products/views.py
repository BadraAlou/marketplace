from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product, Category, SubCategory, UserProfile, Suggestion, BlogPost, ContactMessage
from .forms import ProductForm, UserRegistrationForm, SuggestionForm, ContactForm


def home(request):
    categories = Category.objects.all()[:6]  # Afficher seulement 6 catégories sur la page d'accueil
    return render(request, 'products/home.html', {
        'categories': categories
    })


def pricing(request):
    """Page des tarifs avec les différents packages"""
    packages = [
        {
            'name': 'Small',
            'price': '3 900F',
            'period': '/mois',
            'description': 'Parfait pour commencer',
            'product_limit': '7 produits maximum',
            'color': 'green',
            'popular': False
        },
        {
            'name': 'Medium',
            'price': '5 000F',
            'period': '/mois',
            'description': 'Pour les vendeurs sérieux',
            'product_limit': '20 produits maximum',
            'color': 'navy',
            'popular': True
        },
        {
            'name': 'Large',
            'price': '10 000F',
            'period': '/mois',
            'description': 'Pour les grandes entreprises',
            'product_limit': 'Produits illimités',
            'color': 'purple',
            'popular': False
        }
    ]

    return render(request, 'products/pricing.html', {
        'packages': packages
    })


def conseils(request):
    """Page des conseils pour vendeurs"""
    conseils_posts = [
        {
            'id': 1,
            'title': 'Comment bien photographier vos produits',
            'slug': 'comment-photographier-produits',
            'excerpt': 'La qualité de vos photos détermine en grande partie le succès de vos ventes. Découvrez les techniques simples pour des photos professionnelles.',
            'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '15 janvier 2025',
            'read_time': '5 min',
            'category': 'Photographie'
        },
        {
            'id': 2,
            'title': 'Rédiger des descriptions qui vendent',
            'slug': 'rediger-descriptions-vendues',
            'excerpt': 'Une bonne description transforme un visiteur en acheteur. Apprenez à mettre en valeur vos produits avec les bons mots.',
            'image': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '12 janvier 2025',
            'read_time': '4 min',
            'category': 'Rédaction'
        },
        {
            'id': 3,
            'title': 'Fixer le bon prix pour vos produits',
            'slug': 'fixer-bon-prix-produits',
            'excerpt': 'Ni trop cher, ni trop bon marché. Découvrez comment analyser le marché et positionner vos prix de manière optimale.',
            'image': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '10 janvier 2025',
            'read_time': '6 min',
            'category': 'Stratégie'
        },
        {
            'id': 4,
            'title': 'Gérer efficacement vos commandes',
            'slug': 'gerer-commandes-efficacement',
            'excerpt': 'Organisation, suivi et communication : les clés pour une gestion de commandes sans stress et des clients satisfaits.',
            'image': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '8 janvier 2025',
            'read_time': '7 min',
            'category': 'Gestion'
        },
        {
            'id': 5,
            'title': 'Répondre aux clients rapidement',
            'slug': 'repondre-clients-rapidement',
            'excerpt': 'La réactivité est cruciale dans le commerce en ligne. Conseils pratiques pour un service client efficace.',
            'image': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '5 janvier 2025',
            'read_time': '3 min',
            'category': 'Service Client'
        },
        {
            'id': 6,
            'title': 'Promouvoir vos produits sur les réseaux',
            'slug': 'promouvoir-produits-reseaux-sociaux',
            'excerpt': 'Utilisez Facebook, Instagram et WhatsApp pour augmenter votre visibilité et attirer plus de clients.',
            'image': 'https://images.unsplash.com/photo-1611262588024-d12430b98920?auto=format&fit=crop&w=800&q=80',
            'author': 'Équipe MonMarché',
            'created_at': '3 janvier 2025',
            'read_time': '5 min',
            'category': 'Marketing'
        }
    ]

    return render(request, 'products/conseils.html', {
        'conseils_posts': conseils_posts
    })


def conseil_detail(request, pk):
    """Page de détail d'un conseil"""
    conseils_posts = {
        1: {
            'title': 'Comment bien photographier vos produits',
            'content': '''
            <p>La photographie de produits est l'un des éléments les plus importants pour réussir vos ventes en ligne. Une bonne photo peut faire la différence entre une vente et un client qui passe son chemin.</p>

            <h2>1. Utilisez la lumière naturelle</h2>
            <p>Placez-vous près d'une fenêtre pour bénéficier d'une lumière douce et naturelle. Évitez la lumière directe du soleil qui crée des ombres trop marquées. La lumière du matin ou de fin d'après-midi est idéale.</p>

            <h2>2. Choisissez un arrière-plan neutre</h2>
            <p>Un mur blanc, un drap blanc ou une feuille de papier blanc permettent de mettre en valeur votre produit sans distractions. L'objectif est que le client se concentre uniquement sur votre produit.</p>

            <h2>3. Prenez plusieurs angles</h2>
            <p>Montrez votre produit sous différents angles : face, profil, détails importants. Vos clients veulent voir ce qu'ils achètent. N'hésitez pas à prendre 5 à 8 photos différentes.</p>

            <h2>4. Soignez la mise en scène</h2>
            <p>Pour les vêtements, utilisez un mannequin ou portez-les. Pour les objets, créez un contexte d'utilisation naturel. Montrez le produit en situation d'usage.</p>

            <h2>5. Vérifiez la netteté</h2>
            <p>Assurez-vous que vos photos sont nettes. Une photo floue donne une impression de manque de professionnalisme. Utilisez le mode macro de votre téléphone pour les détails.</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '15 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=1200&q=80',
            'read_time': '5 min',
            'category': 'Photographie'
        },
        2: {
            'title': 'Rédiger des descriptions qui vendent',
            'content': '''
            <p>Une description de produit efficace ne se contente pas de lister les caractéristiques. Elle raconte une histoire, crée une émotion et pousse à l'achat.</p>

            <h2>1. Commencez par les bénéfices</h2>
            <p>Ne listez pas seulement les caractéristiques, expliquez ce que votre produit apporte au client. Par exemple, au lieu de "tissu 100% coton", écrivez "tissu 100% coton pour un confort optimal toute la journée".</p>

            <h2>2. Utilisez des mots sensoriels</h2>
            <p>Aidez vos clients à imaginer le produit : "doux au toucher", "parfum délicat", "couleur éclatante". Ces mots créent une connexion émotionnelle.</p>

            <h2>3. Répondez aux questions</h2>
            <p>Anticipez les questions de vos clients : taille, matière, entretien, utilisation. Plus vous donnez d'informations, plus vous rassurez l'acheteur.</p>

            <h2>4. Créez de l'urgence</h2>
            <p>Mentionnez si c'est une édition limitée, s'il ne reste que quelques pièces, ou si c'est une offre temporaire. Cela pousse à l'action.</p>

            <h2>5. Terminez par un appel à l'action</h2>
            <p>Guidez votre client vers l'étape suivante : "Contactez-moi pour plus d'informations" ou "Disponible immédiatement".</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '12 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1200&q=80',
            'read_time': '4 min',
            'category': 'Rédaction'
        },
        3: {
            'title': 'Fixer le bon prix pour vos produits',
            'content': '''
            <p>Le prix est un élément crucial qui peut faire ou défaire une vente. Trop cher, vous perdez des clients. Trop bon marché, vous perdez de la marge et de la crédibilité.</p>

            <h2>1. Analysez la concurrence</h2>
            <p>Regardez les prix pratiqués pour des produits similaires sur MonMarché et ailleurs. Positionnez-vous en fonction de la qualité de votre offre.</p>

            <h2>2. Calculez vos coûts</h2>
            <p>Prenez en compte le coût d'achat, le temps passé, les frais de transport, et ajoutez votre marge bénéficiaire. N'oubliez pas de valoriser votre travail.</p>

            <h2>3. Testez différents prix</h2>
            <p>N'hésitez pas à ajuster vos prix selon les réactions. Si un produit ne se vend pas, le prix est peut-être trop élevé. Si il part très vite, vous pouvez peut-être augmenter.</p>

            <h2>4. Proposez des gammes de prix</h2>
            <p>Ayez des produits à différents niveaux de prix pour toucher différents types de clients. Du produit d'entrée de gamme au produit premium.</p>

            <h2>5. Justifiez votre prix</h2>
            <p>Expliquez pourquoi votre produit vaut ce prix : qualité supérieure, fabrication artisanale, matériaux nobles, service personnalisé.</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '10 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=1200&q=80',
            'read_time': '6 min',
            'category': 'Stratégie'
        },
        4: {
            'title': 'Gérer efficacement vos commandes',
            'content': '''
            <p>Une bonne gestion des commandes est essentielle pour fidéliser vos clients et développer votre réputation de vendeur fiable.</p>

            <h2>1. Organisez-vous dès le départ</h2>
            <p>Créez un système simple pour suivre vos commandes : un carnet, un fichier Excel, ou une application mobile. L'important est d'être organisé.</p>

            <h2>2. Confirmez rapidement</h2>
            <p>Dès qu'un client vous contacte, confirmez la disponibilité du produit et les modalités de livraison dans les plus brefs délais.</p>

            <h2>3. Communiquez régulièrement</h2>
            <p>Tenez votre client informé : commande reçue, préparation en cours, expédition, livraison. La communication rassure et fidélise.</p>

            <h2>4. Préparez soigneusement</h2>
            <p>Emballez vos produits avec soin. Un bel emballage fait partie de l'expérience client et peut générer des recommandations.</p>

            <h2>5. Suivez après la vente</h2>
            <p>Demandez si le client est satisfait, s'il a des questions. Ce suivi peut déboucher sur de nouvelles ventes ou des recommandations.</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '8 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&q=80',
            'read_time': '7 min',
            'category': 'Gestion'
        },
        5: {
            'title': 'Répondre aux clients rapidement',
            'content': '''
            <p>Dans le commerce en ligne, la rapidité de réponse est cruciale. Un client qui attend trop longtemps ira voir ailleurs.</p>

            <h2>1. Fixez-vous des délais</h2>
            <p>Répondez aux messages dans les 2 heures maximum en journée, et dans les 24h maximum le weekend. Informez vos clients de vos horaires de disponibilité.</p>

            <h2>2. Utilisez les notifications</h2>
            <p>Activez les notifications WhatsApp et email pour être alerté immédiatement quand un client vous contacte.</p>

            <h2>3. Préparez des réponses types</h2>
            <p>Créez des modèles de réponses pour les questions fréquentes : disponibilité, prix, livraison, paiement. Cela vous fait gagner du temps.</p>

            <h2>4. Soyez professionnel mais chaleureux</h2>
            <p>Restez poli et professionnel, mais n'hésitez pas à être chaleureux. Un sourire s'entend même par écrit !</p>

            <h2>5. Si vous ne pouvez pas répondre immédiatement</h2>
            <p>Envoyez au moins un message pour dire que vous avez bien reçu la demande et que vous reviendrez vers le client rapidement.</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '5 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80',
            'read_time': '3 min',
            'category': 'Service Client'
        },
        6: {
            'title': 'Promouvoir vos produits sur les réseaux',
            'content': '''
            <p>Les réseaux sociaux sont un excellent moyen de faire connaître vos produits et d'attirer de nouveaux clients vers votre boutique MonMarché.</p>

            <h2>1. Choisissez les bons réseaux</h2>
            <p>Facebook et Instagram sont parfaits pour montrer vos produits. WhatsApp est idéal pour le contact direct. Concentrez-vous sur 2-3 plateformes maximum.</p>

            <h2>2. Publiez régulièrement</h2>
            <p>Postez au moins 3 fois par semaine. Montrez vos nouveaux produits, vos clients satisfaits, les coulisses de votre activité.</p>

            <h2>3. Utilisez de belles photos</h2>
            <p>Reprenez les conseils de photographie pour créer du contenu attractif. Les visuels sont essentiels sur les réseaux sociaux.</p>

            <h2>4. Interagissez avec votre communauté</h2>
            <p>Répondez aux commentaires, likez les publications de vos clients, partagez du contenu pertinent. Créez une vraie relation.</p>

            <h2>5. Dirigez vers MonMarché</h2>
            <p>Toujours inclure un lien vers votre profil MonMarché dans vos publications. C'est là que se font les ventes !</p>
            ''',
            'author': 'Équipe MonMarché',
            'created_at': '3 janvier 2025',
            'image': 'https://images.unsplash.com/photo-1611262588024-d12430b98920?auto=format&fit=crop&w=1200&q=80',
            'read_time': '5 min',
            'category': 'Marketing'
        }
    }

    conseil = conseils_posts.get(pk)
    if not conseil:
        return redirect('conseils')

    return render(request, 'products/conseil_detail.html', {
        'conseil': conseil
    })


def contact(request):
    """Page de contact avec formulaire"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
            return redirect('contact')
    else:
        form = ContactForm()

    # Informations de contact mises à jour pour le Mali
    contact_info = {
        'email': 'contact@monmarche.fr',
        'phone': '93-07-82-47 / 93-00-58-42',
        'address': 'Bacodjicorni Aci, Mali',
        'hours': 'Lun-Ven: 8h-18h, Sam: 8h-13h'
    }

    return render(request, 'products/contact.html', {
        'form': form,
        'contact_info': contact_info
    })


def about(request):
    """Page À propos avec présentation de l'équipe et de l'entreprise"""
    team = [
        {
            'name': 'Sophie Martin',
            'role': 'CEO & Fondatrice',
            'image': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
            'description': 'Visionnaire et stratège, Sophie dirige l\'entreprise avec passion et 15 ans d\'expérience dans le e-commerce.'
        },
        {
            'name': 'Thomas Dubois',
            'role': 'Directeur Technique',
            'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=800&q=80',
            'description': 'Expert en technologie avec 10 ans d\'expérience, Thomas assure la robustesse et l\'innovation de notre plateforme.'
        },
        {
            'name': 'Marie Lambert',
            'role': 'Responsable Marketing',
            'image': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=800&q=80',
            'description': 'Spécialiste en marketing digital et stratégie de marque, Marie développe notre visibilité et notre communauté.'
        },
        {
            'name': 'Alexandre Chen',
            'role': 'Lead Designer',
            'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=800&q=80',
            'description': 'Créatif passionné par l\'expérience utilisateur, Alexandre conçoit des interfaces intuitives et élégantes.'
        },
        {
            'name': 'Julie Petit',
            'role': 'Service Client',
            'image': 'https://images.unsplash.com/photo-1598550874175-4d0ef436c909?auto=format&fit=crop&w=800&q=80',
            'description': 'Dévouée à offrir une expérience client exceptionnelle, Julie accompagne nos utilisateurs au quotidien.'
        },
        {
            'name': 'David Rodriguez',
            'role': 'Responsable Partenariats',
            'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=800&q=80',
            'description': 'Expert en développement commercial, David noue des partenariats stratégiques pour notre croissance.'
        }
    ]

    return render(request, 'products/about.html', {
        'team': team
    })


def product_list(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    page_number = request.GET.get('page', 1)

    # Initialiser products comme None pour ne rien afficher par défaut
    products = None
    paginator = None
    page_obj = None

    selected_category = None
    selected_subcategory = None

    # Si une recherche est effectuée
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Si une catégorie est sélectionnée
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=selected_category)

        # Limiter à 4 produits pour la catégorie (sans sous-catégorie)
        if not subcategory_slug:
            products = products[:4]

        # Si une sous-catégorie est sélectionnée
        if subcategory_slug:
            selected_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=selected_category)
            products = Product.objects.filter(subcategory=selected_subcategory)

            # Pagination pour les sous-catégories (20 produits par page)
            paginator = Paginator(products, 20)
            page_obj = paginator.get_page(page_number)
            products = page_obj

    categories = Category.objects.all()
    subcategories = []

    if selected_category:
        subcategories = selected_category.subcategories.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
        'query': query,
        'page_obj': page_obj,
        'paginator': paginator,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {
        'product': product
    })


@login_required
def dashboard(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_seller:
        messages.error(request, 'Accès réservé aux vendeurs')
        return redirect('home')

    if not request.user.userprofile.is_seller_validated:
        messages.warning(request, 'Votre compte vendeur est en attente de validation par un administrateur.')
        return redirect('home')

    if not request.user.userprofile.is_subscription_active:
        messages.error(request, 'Votre abonnement n\'est pas actif. Contactez l\'administration.')
        return redirect('home')

    profile = request.user.userprofile
    products = Product.objects.filter(seller=request.user)

    return render(request, 'products/dashboard.html', {
        'products': products,
        'profile': profile,
        'current_count': profile.current_product_count,
        'product_limit': profile.product_limit,
        'remaining_products': profile.remaining_products,
        'can_add_product': profile.can_add_product,
    })


@login_required
def product_create(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_seller:
        messages.error(request, 'Seuls les vendeurs peuvent ajouter des produits')
        return redirect('home')

    if not request.user.userprofile.is_seller_validated:
        messages.warning(request,
                         'Votre compte vendeur doit être validé par un administrateur avant de pouvoir ajouter des produits.')
        return redirect('home')

    if not request.user.userprofile.is_subscription_active:
        messages.error(request, 'Votre abonnement n\'est pas actif. Contactez l\'administration.')
        return redirect('home')

    profile = request.user.userprofile

    # Vérifier la limite de produits
    if not profile.can_add_product:
        limit = profile.product_limit
        current = profile.current_product_count

        if limit is None:
            messages.error(request, 'Une erreur est survenue. Contactez l\'administration.')
        else:
            messages.error(request,
                           f'Vous avez atteint votre limite de {limit} produits ({current}/{limit}). '
                           f'Mettez à niveau votre abonnement pour ajouter plus de produits.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Vérifier à nouveau la limite avant de sauvegarder
            if not profile.can_add_product:
                messages.error(request, 'Limite de produits atteinte.')
                return redirect('dashboard')

            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            remaining = profile.remaining_products
            if remaining != "Illimité" and remaining <= 2:
                messages.warning(request,
                                 f'Produit ajouté avec succès! Attention: il ne vous reste que {remaining} produit(s) à ajouter.')
            else:
                messages.success(request, 'Produit ajouté avec succès!')
            return redirect('dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Ajouter un produit',
        'profile': profile,
        'remaining_products': profile.remaining_products,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.userprofile.is_seller:
                messages.info(request,
                              'Votre compte vendeur a été créé. Un administrateur doit valider votre compte avant que vous puissiez ajouter des produits.')
            else:
                messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {
        'form': form
    })


def load_subcategories(request):
    """Vue AJAX pour charger les sous-catégories en fonction de la catégorie sélectionnée"""
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)