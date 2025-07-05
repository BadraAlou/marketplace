from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, UserProfile, Suggestion, Category, SubCategory, ContactMessage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'name', 'description', 'price', 'image', 'whatsapp', 'email']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'subcategory': forms.Select(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'whatsapp': forms.TextInput(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by(
                    'name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.order_by('name')


class UserRegistrationForm(UserCreationForm):
    is_seller = forms.BooleanField(required=False, label='Je souhaite devenir vendeur')
    subscription_plan = forms.ChoiceField(
        choices=UserProfile.SUBSCRIPTION_CHOICES,
        initial='small',
        label='Plan d\'abonnement',
        help_text='Choisissez votre plan d\'abonnement (vous pourrez le modifier plus tard)'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_seller', 'subscription_plan']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                is_seller=self.cleaned_data['is_seller'],
                subscription_plan=self.cleaned_data['subscription_plan']
            )
        return user


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white',
                'placeholder': 'votre.email@exemple.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white',
                'placeholder': 'Sujet de votre message'
            }),
            'message': forms.Textarea(attrs={
                'rows': 6,
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white',
                'placeholder': 'Décrivez votre demande en détail...'
            })
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 neo-brutalist-sm bg-white'
            })
        }