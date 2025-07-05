from django.core.management.base import BaseCommand
from products.models import Category, SubCategory


class Command(BaseCommand):
    help = 'Creates initial categories and subcategories'

    def handle(self, *args, **kwargs):
        # Définition des catégories et sous-catégories
        categories_data = {
            'Électroménager': {
                'icon': 'zap',
                'description': 'Appareils électroménagers pour la maison',
                'subcategories': [
                    'Réfrigérateurs',
                    'Lave-linge',
                    'Lave-vaisselle',
                    'Fours et Micro-ondes',
                    'Aspirateurs',
                    'Cafetières',
                    'Mixeurs et Blenders',
                    'Grille-pain',
                ]
            },
            'Vêtements': {
                'icon': 'shirt',
                'description': 'Mode et vêtements pour tous',
                'subcategories': [
                    'Vestes et Manteaux',
                    'Robes',
                    'Pantalons',
                    'Chemises et Blouses',
                    'T-shirts et Tops',
                    'Jupes',
                    'Sous-vêtements',
                    'Chaussures',
                ]
            },
            'Accessoires': {
                'icon': 'watch',
                'description': 'Accessoires de mode et bijoux',
                'subcategories': [
                    'Montres',
                    'Chaînes et Colliers',
                    'Bracelets',
                    'Bagues',
                    'Boucles d\'oreilles',
                    'Sacs à main',
                    'Ceintures',
                    'Lunettes',
                ]
            },
            'Électronique': {
                'icon': 'smartphone',
                'description': 'Appareils électroniques et high-tech',
                'subcategories': [
                    'Smartphones',
                    'Ordinateurs portables',
                    'Tablettes',
                    'Écouteurs et Casques',
                    'Appareils photo',
                    'Télévisions',
                    'Consoles de jeux',
                    'Accessoires tech',
                ]
            },
            'Maison et Jardin': {
                'icon': 'home',
                'description': 'Tout pour la maison et le jardin',
                'subcategories': [
                    'Meubles',
                    'Décoration',
                    'Éclairage',
                    'Textiles de maison',
                    'Outils de jardinage',
                    'Plantes',
                    'Barbecue et Plancha',
                    'Piscine et Spa',
                ]
            },
            'Sport et Loisirs': {
                'icon': 'dumbbell',
                'description': 'Équipements sportifs et loisirs',
                'subcategories': [
                    'Fitness et Musculation',
                    'Vélos',
                    'Sports d\'eau',
                    'Sports d\'hiver',
                    'Football',
                    'Tennis',
                    'Course à pied',
                    'Camping et Randonnée',
                ]
            },
            'Alimentation': {
                'icon': 'apple',
                'description': 'Produits alimentaires et boissons',
                'subcategories': [
                    'Fruits et Légumes',
                    'Viandes et Poissons',
                    'Produits laitiers',
                    'Épicerie salée',
                    'Épicerie sucrée',
                    'Boissons',
                    'Produits bio',
                    'Surgelés',
                ]
            },
            'Beauté et Santé': {
                'icon': 'heart',
                'description': 'Produits de beauté et de santé',
                'subcategories': [
                    'Soins du visage',
                    'Soins du corps',
                    'Maquillage',
                    'Parfums',
                    'Soins des cheveux',
                    'Hygiène',
                    'Compléments alimentaires',
                    'Matériel médical',
                ]
            }
        }

        for category_name, category_info in categories_data.items():
            # Créer ou récupérer la catégorie
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': category_name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e'),
                    'icon': category_info['icon'],
                    'description': category_info['description']
                }
            )

            if created:
                self.stdout.write(f'Catégorie créée: {category_name}')

            # Créer les sous-catégories
            for subcategory_name in category_info['subcategories']:
                subcategory, sub_created = SubCategory.objects.get_or_create(
                    category=category,
                    name=subcategory_name,
                    defaults={
                        'slug': subcategory_name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e').replace(
                            '\'', '')
                    }
                )

                if sub_created:
                    self.stdout.write(f'  Sous-catégorie créée: {subcategory_name}')

        self.stdout.write(self.style.SUCCESS('Catégories et sous-catégories créées avec succès!'))