from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta
import uuid


class Employee(models.Model):
    """Modèle autonome pour les employés - indépendant du système User de Django"""
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Célibataire'),
        ('married', 'Marié(e)'),
        ('divorced', 'Divorcé(e)'),
        ('widowed', 'Veuf/Veuve'),
        ('partnership', 'Union libre'),
    ]

    DEPARTMENT_CHOICES = [
        ('admin', 'Administration'),
        ('tech', 'Technique'),
        ('marketing', 'Marketing'),
        ('sales', 'Ventes'),
        ('support', 'Support Client'),
        ('finance', 'Finance'),
        ('hr', 'Ressources Humaines'),
        ('logistics', 'Logistique'),
        ('production', 'Production'),
        ('quality', 'Qualité'),
        ('legal', 'Juridique'),
        ('communication', 'Communication'),
    ]

    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('on_leave', 'En congé'),
        ('terminated', 'Licencié'),
        ('retired', 'Retraité'),
        ('suspended', 'Suspendu'),
        ('probation', 'Période d\'essai'),
    ]

    CONTRACT_CHOICES = [
        ('cdi', 'CDI - Contrat à Durée Indéterminée'),
        ('cdd', 'CDD - Contrat à Durée Déterminée'),
        ('stage', 'Stage'),
        ('apprentissage', 'Contrat d\'apprentissage'),
        ('freelance', 'Freelance'),
        ('consultant', 'Consultant'),
        ('interim', 'Intérim'),
        ('volontariat', 'Volontariat'),
    ]

    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primaire'),
        ('secondary', 'Secondaire'),
        ('bac', 'Baccalauréat'),
        ('bac_plus_2', 'Bac+2'),
        ('bac_plus_3', 'Bac+3 (Licence)'),
        ('bac_plus_5', 'Bac+5 (Master)'),
        ('doctorate', 'Doctorat'),
        ('other', 'Autre'),
    ]

    # Informations personnelles de base
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="ID Employé")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom de famille")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Deuxième prénom")
    maiden_name = models.CharField(max_length=50, blank=True, verbose_name="Nom de jeune fille")

    # Contact
    email = models.EmailField(unique=True, verbose_name="Email professionnel")
    personal_email = models.EmailField(blank=True, verbose_name="Email personnel")
    phone = models.CharField(max_length=20, verbose_name="Téléphone principal")
    mobile_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone mobile")
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")

    # Informations personnelles détaillées
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    place_of_birth = models.CharField(max_length=100, verbose_name="Lieu de naissance")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Genre")
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, verbose_name="Statut marital")
    nationality = models.CharField(max_length=50, verbose_name="Nationalité")
    id_number = models.CharField(max_length=50, verbose_name="Numéro de pièce d'identité")
    passport_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de passeport")
    social_security_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de sécurité sociale")

    # Adresse principale
    address = models.TextField(verbose_name="Adresse complète")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=20, verbose_name="Code postal")
    country = models.CharField(max_length=50, default="Côte d'Ivoire", verbose_name="Pays")

    # Adresse secondaire (optionnelle)
    secondary_address = models.TextField(blank=True, verbose_name="Adresse secondaire")
    secondary_city = models.CharField(max_length=100, blank=True, verbose_name="Ville secondaire")
    secondary_postal_code = models.CharField(max_length=20, blank=True, verbose_name="Code postal secondaire")

    # Informations professionnelles
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, verbose_name="Département")
    position = models.CharField(max_length=100, verbose_name="Poste")
    job_description = models.TextField(blank=True, verbose_name="Description du poste")
    hire_date = models.DateField(verbose_name="Date d'embauche")
    probation_end_date = models.DateField(null=True, blank=True, verbose_name="Fin de période d'essai")
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, verbose_name="Type de contrat")
    contract_start_date = models.DateField(verbose_name="Début de contrat")
    contract_end_date = models.DateField(null=True, blank=True, verbose_name="Fin de contrat (si CDD)")

    # Hiérarchie
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='subordinates', verbose_name="Manager direct")

    # Salaire et avantages
    salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire mensuel (F CFA)")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                      verbose_name="Taux horaire")
    overtime_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                        verbose_name="Taux heures sup.")

    # Horaires de travail
    work_schedule = models.CharField(max_length=100, default="Lun-Ven 8h-17h", verbose_name="Horaires de travail")
    weekly_hours = models.PositiveIntegerField(default=40, verbose_name="Heures hebdomadaires")

    # Statut et état
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='probation', verbose_name="Statut")
    termination_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    termination_reason = models.TextField(blank=True, verbose_name="Motif de fin de contrat")

    # Informations bancaires
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Nom de la banque")
    bank_account = models.CharField(max_length=50, blank=True, verbose_name="Numéro de compte")
    iban = models.CharField(max_length=50, blank=True, verbose_name="IBAN")
    swift_code = models.CharField(max_length=20, blank=True, verbose_name="Code SWIFT")

    # Éducation
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES,
                                       blank=True, verbose_name="Niveau d'éducation")
    university = models.CharField(max_length=200, blank=True, verbose_name="Université/École")
    degree = models.CharField(max_length=200, blank=True, verbose_name="Diplôme")
    graduation_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Année d'obtention")

    # Contacts d'urgence (multiples)
    emergency_contact_1_name = models.CharField(max_length=100, verbose_name="Contact d'urgence 1 - Nom")
    emergency_contact_1_phone = models.CharField(max_length=20, verbose_name="Contact d'urgence 1 - Téléphone")
    emergency_contact_1_relationship = models.CharField(max_length=50, verbose_name="Lien de parenté 1")

    emergency_contact_2_name = models.CharField(max_length=100, blank=True, verbose_name="Contact d'urgence 2 - Nom")
    emergency_contact_2_phone = models.CharField(max_length=20, blank=True,
                                                 verbose_name="Contact d'urgence 2 - Téléphone")
    emergency_contact_2_relationship = models.CharField(max_length=50, blank=True, verbose_name="Lien de parenté 2")

    # Informations médicales
    blood_type = models.CharField(max_length=5, blank=True, verbose_name="Groupe sanguin")
    allergies = models.TextField(blank=True, verbose_name="Allergies")
    medical_conditions = models.TextField(blank=True, verbose_name="Conditions médicales")
    medical_insurance_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro assurance maladie")

    # Compétences et langues
    skills = models.TextField(blank=True, verbose_name="Compétences")
    languages = models.TextField(blank=True, verbose_name="Langues parlées")
    certifications = models.TextField(blank=True, verbose_name="Certifications")

    # Informations supplémentaires
    photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True, verbose_name="Photo")
    signature = models.ImageField(upload_to='employees/signatures/', blank=True, null=True, verbose_name="Signature")
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Préférences
    preferred_communication = models.CharField(max_length=20,
                                               choices=[('email', 'Email'), ('phone', 'Téléphone'),
                                                        ('whatsapp', 'WhatsApp')],
                                               default='email', verbose_name="Communication préférée")

    # Suivi et audit
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="Créé par")
    last_modified_by = models.CharField(max_length=100, blank=True, verbose_name="Modifié par")

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def years_of_service(self):
        today = date.today()
        return today.year - self.hire_date.year - (
                    (today.month, today.day) < (self.hire_date.month, self.hire_date.day))

    @property
    def is_on_probation(self):
        if self.probation_end_date:
            return date.today() <= self.probation_end_date
        return self.status == 'probation'

    @property
    def contract_expires_soon(self):
        if self.contract_end_date:
            return (self.contract_end_date - date.today()).days <= 30
        return False


class Intern(models.Model):
    """Modèle spécifique pour les stagiaires"""
    INTERNSHIP_TYPE_CHOICES = [
        ('observation', 'Stage d\'observation'),
        ('application', 'Stage d\'application'),
        ('professional', 'Stage professionnel'),
        ('graduation', 'Stage de fin d\'études'),
        ('voluntary', 'Stage volontaire'),
    ]

    STATUS_CHOICES = [
        ('active', 'En cours'),
        ('completed', 'Terminé'),
        ('terminated', 'Interrompu'),
        ('extended', 'Prolongé'),
    ]

    # Informations de base
    intern_id = models.CharField(max_length=20, unique=True, verbose_name="ID Stagiaire")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom de famille")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    date_of_birth = models.DateField(verbose_name="Date de naissance")

    # Adresse
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=20, verbose_name="Code postal")

    # Informations académiques
    school = models.CharField(max_length=200, verbose_name="École/Université")
    field_of_study = models.CharField(max_length=200, verbose_name="Domaine d'études")
    academic_level = models.CharField(max_length=100, verbose_name="Niveau académique")
    academic_year = models.CharField(max_length=20, verbose_name="Année académique")

    # Informations de stage
    internship_type = models.CharField(max_length=20, choices=INTERNSHIP_TYPE_CHOICES, verbose_name="Type de stage")
    department = models.CharField(max_length=20, choices=Employee.DEPARTMENT_CHOICES, verbose_name="Département")
    supervisor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                   related_name='supervised_interns', verbose_name="Superviseur")

    # Dates et durée
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    duration_weeks = models.PositiveIntegerField(verbose_name="Durée en semaines")

    # Objectifs et évaluation
    objectives = models.TextField(verbose_name="Objectifs du stage")
    tasks_assigned = models.TextField(blank=True, verbose_name="Tâches assignées")

    # Rémunération
    is_paid = models.BooleanField(default=False, verbose_name="Stage rémunéré")
    monthly_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Indemnité mensuelle")

    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")

    # Contact d'urgence
    emergency_contact_name = models.CharField(max_length=100, verbose_name="Contact d'urgence - Nom")
    emergency_contact_phone = models.CharField(max_length=20, verbose_name="Contact d'urgence - Téléphone")
    emergency_contact_relationship = models.CharField(max_length=50, verbose_name="Lien de parenté")

    # Documents et évaluation
    convention_signed = models.BooleanField(default=False, verbose_name="Convention signée")
    final_report_submitted = models.BooleanField(default=False, verbose_name="Rapport final soumis")
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                      verbose_name="Note finale (/20)")

    # Suivi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="Créé par")

    class Meta:
        verbose_name = "Stagiaire"
        verbose_name_plural = "Stagiaires"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.intern_id} - {self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def days_remaining(self):
        if self.status == 'active':
            return (self.end_date - date.today()).days
        return 0

    @property
    def progress_percentage(self):
        if self.status != 'active':
            return 100 if self.status == 'completed' else 0

        total_days = (self.end_date - self.start_date).days
        elapsed_days = (date.today() - self.start_date).days
        return min(100, max(0, (elapsed_days / total_days) * 100))


class Department(models.Model):
    """Modèle pour les départements"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du département")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='managed_department', verbose_name="Responsable")
    assistant_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='assistant_managed_department',
                                          verbose_name="Responsable adjoint")
    description = models.TextField(blank=True, verbose_name="Description")
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                 verbose_name="Budget annuel (F CFA)")
    location = models.CharField(max_length=200, blank=True, verbose_name="Localisation")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du département")
    email = models.EmailField(blank=True, verbose_name="Email du département")

    # Objectifs et KPIs
    objectives = models.TextField(blank=True, verbose_name="Objectifs du département")
    kpis = models.TextField(blank=True, verbose_name="Indicateurs de performance")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def employee_count(self):
        return Employee.objects.filter(department=self.code.lower(), status='active').count()

    @property
    def intern_count(self):
        return Intern.objects.filter(department=self.code.lower(), status='active').count()


class LeaveRequest(models.Model):
    """Modèle pour les demandes de congé"""
    LEAVE_TYPES = [
        ('vacation', 'Congés payés'),
        ('sick', 'Congé maladie'),
        ('personal', 'Congé personnel'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
        ('bereavement', 'Congé de deuil'),
        ('training', 'Formation'),
        ('compensatory', 'Récupération'),
        ('unpaid', 'Congé sans solde'),
        ('sabbatical', 'Congé sabbatique'),
        ('other', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevée'),
        ('urgent', 'Urgent'),
    ]

    # Informations de base
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID Demande")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, verbose_name="Type de congé")

    # Dates et durée
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    days_requested = models.PositiveIntegerField(verbose_name="Nombre de jours")
    half_day_start = models.BooleanField(default=False, verbose_name="Demi-journée début")
    half_day_end = models.BooleanField(default=False, verbose_name="Demi-journée fin")

    # Détails de la demande
    reason = models.TextField(verbose_name="Motif")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name="Priorité")
    supporting_documents = models.FileField(upload_to='leave_requests/', blank=True, null=True,
                                            verbose_name="Documents justificatifs")

    # Remplacement
    replacement_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='replacement_leaves', verbose_name="Remplaçant")
    handover_notes = models.TextField(blank=True, verbose_name="Notes de passation")

    # Statut et approbation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_leaves', verbose_name="Approuvé par")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de refus")

    # Commentaires et suivi
    comments = models.TextField(blank=True, verbose_name="Commentaires")
    hr_comments = models.TextField(blank=True, verbose_name="Commentaires RH")

    # Suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congé"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} - {self.end_date})"

    @property
    def is_current(self):
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == 'approved'

    @property
    def days_until_start(self):
        return (self.start_date - date.today()).days


class Attendance(models.Model):
    """Modèle pour la gestion des présences"""
    ATTENDANCE_STATUS = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
        ('half_day', 'Demi-journée'),
        ('on_leave', 'En congé'),
        ('sick', 'Malade'),
        ('remote', 'Télétravail'),
        ('business_trip', 'Déplacement professionnel'),
        ('training', 'Formation'),
    ]

    # Informations de base
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    date = models.DateField(verbose_name="Date")

    # Horaires
    check_in = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivée")
    check_out = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    break_start = models.TimeField(null=True, blank=True, verbose_name="Début de pause")
    break_end = models.TimeField(null=True, blank=True, verbose_name="Fin de pause")

    # Calculs automatiques
    total_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                      verbose_name="Heures totales")
    break_duration = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name="Durée de pause (h)")
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                         verbose_name="Heures supplémentaires")
    late_minutes = models.PositiveIntegerField(default=0, verbose_name="Minutes de retard")

    # Statut et justification
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='present', verbose_name="Statut")
    is_justified = models.BooleanField(default=True, verbose_name="Justifié")
    justification = models.TextField(blank=True, verbose_name="Justification")

    # Localisation (pour le télétravail)
    work_location = models.CharField(max_length=200, blank=True, verbose_name="Lieu de travail")

    # Notes et validation
    notes = models.TextField(blank=True, verbose_name="Notes")
    validated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='validated_attendances', verbose_name="Validé par")
    validation_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Calcul automatique des heures
        if self.check_in and self.check_out:
            from datetime import datetime, timedelta

            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)

            # Si check_out est le lendemain
            if self.check_out < self.check_in:
                check_out_dt += timedelta(days=1)

            total_time = check_out_dt - check_in_dt

            # Soustraire la pause
            if self.break_start and self.break_end:
                break_start_dt = datetime.combine(self.date, self.break_start)
                break_end_dt = datetime.combine(self.date, self.break_end)
                break_time = break_end_dt - break_start_dt
                self.break_duration = break_time.total_seconds() / 3600
                total_time -= break_time

            self.total_hours = total_time.total_seconds() / 3600

            # Calcul des heures supplémentaires (au-delà de 8h)
            if self.total_hours > 8:
                self.overtime_hours = self.total_hours - 8

        super().save(*args, **kwargs)


class Payroll(models.Model):
    """Modèle pour la gestion de la paie"""
    PAYMENT_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('calculated', 'Calculé'),
        ('approved', 'Approuvé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Virement bancaire'),
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
        ('mobile_money', 'Mobile Money'),
    ]

    # Informations de base
    payroll_id = models.CharField(max_length=20, unique=True, verbose_name="ID Paie")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mois")
    year = models.PositiveIntegerField(verbose_name="Année")

    # Période de travail
    work_days = models.PositiveIntegerField(default=22, verbose_name="Jours travaillés")
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Heures totales")
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                         verbose_name="Heures supplémentaires")

    # Salaire de base
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire de base")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                      verbose_name="Taux horaire")

    # Primes et indemnités
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              verbose_name="Indemnité transport")
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité repas")
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Indemnité logement")
    family_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           verbose_name="Allocations familiales")
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Prime de performance")
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       verbose_name="Heures supplémentaires")
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Commissions")
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres primes")

    # Déductions obligatoires
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Sécurité sociale")
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impôt sur le revenu")
    pension_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                               verbose_name="Cotisation retraite")

    # Déductions volontaires
    advance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Avance sur salaire")
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Remboursement prêt")
    insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Assurance")
    union_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cotisation syndicale")
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres déductions")

    # Totaux calculés automatiquement
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire brut")
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total primes")
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total déductions")
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Revenu imposable")
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Salaire net")

    # Statut et paiement
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='draft', verbose_name="Statut")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True,
                                      verbose_name="Mode de paiement")
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name="Référence de paiement")

    # Validation et approbation
    calculated_by = models.CharField(max_length=100, blank=True, verbose_name="Calculé par")
    approved_by = models.CharField(max_length=100, blank=True, verbose_name="Approuvé par")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")

    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fiche de paie"
        verbose_name_plural = "Fiches de paie"
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month', 'employee']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.month:02d}/{self.year}"

    def save(self, *args, **kwargs):
        # Génération automatique de l'ID paie
        if not self.payroll_id:
            self.payroll_id = f"PAY-{self.year}-{self.month:02d}-{self.employee.employee_id}"

        # Calcul automatique des totaux
        self.total_allowances = (
                self.transport_allowance + self.meal_allowance + self.housing_allowance +
                self.family_allowance + self.performance_bonus + self.overtime_pay +
                self.commission + self.other_allowances
        )

        self.gross_salary = self.base_salary + self.total_allowances

        self.total_deductions = (
                self.social_security + self.income_tax + self.pension_contribution +
                self.advance_deduction + self.loan_deduction + self.insurance_deduction +
                self.union_dues + self.other_deductions
        )

        self.taxable_income = self.gross_salary - self.social_security - self.pension_contribution
        self.net_salary = self.gross_salary - self.total_deductions

        super().save(*args, **kwargs)


class Performance(models.Model):
    """Modèle pour l'évaluation des performances"""
    RATING_CHOICES = [
        (1, 'Insuffisant'),
        (2, 'Satisfaisant'),
        (3, 'Bien'),
        (4, 'Très bien'),
        (5, 'Excellent'),
    ]

    EVALUATION_TYPE_CHOICES = [
        ('annual', 'Évaluation annuelle'),
        ('probation', 'Fin de période d\'essai'),
        ('mid_year', 'Mi-parcours'),
        ('project', 'Fin de projet'),
        ('promotion', 'Promotion'),
        ('disciplinary', 'Disciplinaire'),
    ]

    # Informations de base
    evaluation_id = models.CharField(max_length=20, unique=True, verbose_name="ID Évaluation")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    evaluator = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations_given',
                                  verbose_name="Évaluateur")
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES, verbose_name="Type d'évaluation")

    # Période d'évaluation
    period_start = models.DateField(verbose_name="Début de période")
    period_end = models.DateField(verbose_name="Fin de période")
    evaluation_date = models.DateField(verbose_name="Date d'évaluation")

    # Critères d'évaluation détaillés
    overall_rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Note globale")

    # Compétences techniques
    technical_skills = models.IntegerField(choices=RATING_CHOICES, verbose_name="Compétences techniques")
    job_knowledge = models.IntegerField(choices=RATING_CHOICES, verbose_name="Connaissance du poste")
    quality_of_work = models.IntegerField(choices=RATING_CHOICES, verbose_name="Qualité du travail")
    productivity = models.IntegerField(choices=RATING_CHOICES, verbose_name="Productivité")
    innovation = models.IntegerField(choices=RATING_CHOICES, verbose_name="Innovation")

    # Compétences comportementales
    communication = models.IntegerField(choices=RATING_CHOICES, verbose_name="Communication")
    teamwork = models.IntegerField(choices=RATING_CHOICES, verbose_name="Travail d'équipe")
    leadership = models.IntegerField(choices=RATING_CHOICES, verbose_name="Leadership")
    initiative = models.IntegerField(choices=RATING_CHOICES, verbose_name="Initiative")
    adaptability = models.IntegerField(choices=RATING_CHOICES, verbose_name="Adaptabilité")

    # Attitude et comportement
    punctuality = models.IntegerField(choices=RATING_CHOICES, verbose_name="Ponctualité")
    reliability = models.IntegerField(choices=RATING_CHOICES, verbose_name="Fiabilité")
    professionalism = models.IntegerField(choices=RATING_CHOICES, verbose_name="Professionnalisme")
    customer_service = models.IntegerField(choices=RATING_CHOICES, verbose_name="Service client")
    problem_solving = models.IntegerField(choices=RATING_CHOICES, verbose_name="Résolution de problèmes")

    # Objectifs et résultats
    objectives_met = models.TextField(verbose_name="Objectifs atteints")
    objectives_missed = models.TextField(blank=True, verbose_name="Objectifs non atteints")
    key_achievements = models.TextField(verbose_name="Réalisations clés")

    # Commentaires détaillés
    strengths = models.TextField(verbose_name="Points forts")
    areas_for_improvement = models.TextField(verbose_name="Axes d'amélioration")
    development_plan = models.TextField(verbose_name="Plan de développement")
    goals_next_period = models.TextField(verbose_name="Objectifs pour la prochaine période")

    # Commentaires des parties
    evaluator_comments = models.TextField(verbose_name="Commentaires de l'évaluateur")
    employee_comments = models.TextField(blank=True, verbose_name="Commentaires de l'employé")
    hr_comments = models.TextField(blank=True, verbose_name="Commentaires RH")

    # Recommandations
    salary_increase_recommended = models.BooleanField(default=False, verbose_name="Augmentation recommandée")
    salary_increase_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                     verbose_name="Pourcentage d'augmentation (%)")
    promotion_recommended = models.BooleanField(default=False, verbose_name="Promotion recommandée")
    promotion_position = models.CharField(max_length=100, blank=True, verbose_name="Poste de promotion")
    training_recommended = models.TextField(blank=True, verbose_name="Formations recommandées")

    # Signatures et validation
    employee_signature_date = models.DateField(null=True, blank=True, verbose_name="Date signature employé")
    evaluator_signature_date = models.DateField(null=True, blank=True, verbose_name="Date signature évaluateur")
    hr_approval_date = models.DateField(null=True, blank=True, verbose_name="Date approbation RH")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Évaluation de performance"
        verbose_name_plural = "Évaluations de performance"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_evaluation_type_display()} ({self.period_start} - {self.period_end})"

    @property
    def average_rating(self):
        ratings = [
            self.technical_skills, self.job_knowledge, self.quality_of_work, self.productivity,
            self.innovation, self.communication, self.teamwork, self.leadership, self.initiative,
            self.adaptability, self.punctuality, self.reliability, self.professionalism,
            self.customer_service, self.problem_solving
        ]
        return sum(ratings) / len(ratings)

    @property
    def is_completed(self):
        return (self.employee_signature_date is not None and
                self.evaluator_signature_date is not None)


class Training(models.Model):
    """Modèle pour les formations"""
    TRAINING_STATUS = [
        ('planned', 'Planifiée'),
        ('registration_open', 'Inscriptions ouvertes'),
        ('registration_closed', 'Inscriptions fermées'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('postponed', 'Reportée'),
    ]

    TRAINING_TYPE = [
        ('internal', 'Formation interne'),
        ('external', 'Formation externe'),
        ('online', 'Formation en ligne'),
        ('workshop', 'Atelier'),
        ('seminar', 'Séminaire'),
        ('conference', 'Conférence'),
        ('certification', 'Certification'),
        ('mentoring', 'Mentorat'),
    ]

    TRAINING_CATEGORY = [
        ('technical', 'Technique'),
        ('management', 'Management'),
        ('soft_skills', 'Compétences comportementales'),
        ('safety', 'Sécurité'),
        ('compliance', 'Conformité'),
        ('language', 'Langues'),
        ('it', 'Informatique'),
        ('sales', 'Vente'),
        ('customer_service', 'Service client'),
        ('other', 'Autre'),
    ]

    # Informations de base
    training_id = models.CharField(max_length=20, unique=True, verbose_name="ID Formation")
    title = models.CharField(max_length=200, verbose_name="Titre de la formation")
    description = models.TextField(verbose_name="Description")
    training_type = models.CharField(max_length=20, choices=TRAINING_TYPE, verbose_name="Type de formation")
    category = models.CharField(max_length=20, choices=TRAINING_CATEGORY, verbose_name="Catégorie")

    # Organisateur et formateur
    trainer = models.CharField(max_length=100, verbose_name="Formateur/Organisme")
    trainer_bio = models.TextField(blank=True, verbose_name="Biographie du formateur")
    training_provider = models.CharField(max_length=200, blank=True, verbose_name="Organisme de formation")

    # Planning
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    duration_hours = models.PositiveIntegerField(verbose_name="Durée en heures")
    schedule = models.TextField(blank=True, verbose_name="Planning détaillé")

    # Lieu et modalités
    location = models.CharField(max_length=200, verbose_name="Lieu")
    is_online = models.BooleanField(default=False, verbose_name="Formation en ligne")
    platform_url = models.URLField(blank=True, verbose_name="URL de la plateforme")
    meeting_link = models.URLField(blank=True, verbose_name="Lien de réunion")

    # Participants
    max_participants = models.PositiveIntegerField(verbose_name="Nombre max de participants")
    min_participants = models.PositiveIntegerField(default=1, verbose_name="Nombre min de participants")
    target_audience = models.TextField(verbose_name="Public cible")

    # Coûts
    cost_per_participant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Coût par participant")
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Budget total")
    additional_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           verbose_name="Coûts additionnels")

    # Contenu pédagogique
    objectives = models.TextField(verbose_name="Objectifs de la formation")
    learning_outcomes = models.TextField(verbose_name="Résultats d'apprentissage attendus")
    prerequisites = models.TextField(blank=True, verbose_name="Prérequis")
    curriculum = models.TextField(verbose_name="Programme détaillé")
    materials_provided = models.TextField(blank=True, verbose_name="Matériel fourni")

    # Évaluation
    has_assessment = models.BooleanField(default=False, verbose_name="Évaluation incluse")
    assessment_method = models.CharField(max_length=200, blank=True, verbose_name="Méthode d'évaluation")
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                        verbose_name="Score de réussite (%)")
    certification_provided = models.BooleanField(default=False, verbose_name="Certification fournie")

    # Statut et suivi
    status = models.CharField(max_length=20, choices=TRAINING_STATUS, default='planned', verbose_name="Statut")
    registration_deadline = models.DateField(null=True, blank=True, verbose_name="Date limite d'inscription")

    # Responsable formation
    training_coordinator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='coordinated_trainings',
                                             verbose_name="Coordinateur formation")

    participants = models.ManyToManyField(Employee, through='TrainingParticipation', verbose_name="Participants")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d/%m/%Y')}"

    @property
    def current_participants(self):
        return self.participants.count()

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def registration_open(self):
        if self.registration_deadline:
            return date.today() <= self.registration_deadline
        return self.status == 'registration_open'


class TrainingParticipation(models.Model):
    """Modèle pour la participation aux formations"""
    PARTICIPATION_STATUS = [
        ('registered', 'Inscrit'),
        ('confirmed', 'Confirmé'),
        ('attended', 'Présent'),
        ('absent', 'Absent'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('withdrawn', 'Désisté'),
    ]

    # Informations de base
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    training = models.ForeignKey(Training, on_delete=models.CASCADE, verbose_name="Formation")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS, default='registered', verbose_name="Statut")

    # Motivation et objectifs
    motivation = models.TextField(blank=True, verbose_name="Motivation pour cette formation")
    personal_objectives = models.TextField(blank=True, verbose_name="Objectifs personnels")

    # Présence et participation
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                verbose_name="Taux de présence (%)")
    participation_quality = models.IntegerField(choices=Performance.RATING_CHOICES, null=True, blank=True,
                                                verbose_name="Qualité de participation")

    # Évaluation et résultats
    pre_training_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                             verbose_name="Score pré-formation (%)")
    post_training_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                              verbose_name="Score post-formation (%)")
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      verbose_name="Score final (%)")

    # Certification
    certificate_issued = models.BooleanField(default=False, verbose_name="Certificat délivré")
    certificate_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de certificat")
    certificate_date = models.DateField(null=True, blank=True, verbose_name="Date du certificat")
    certificate_expiry = models.DateField(null=True, blank=True, verbose_name="Expiration du certificat")

    # Feedback et évaluation
    participant_feedback = models.TextField(blank=True, verbose_name="Commentaires du participant")
    trainer_feedback = models.TextField(blank=True, verbose_name="Commentaires du formateur")
    training_rating = models.IntegerField(choices=Performance.RATING_CHOICES, null=True, blank=True,
                                          verbose_name="Note de la formation")

    # Application des acquis
    knowledge_application = models.TextField(blank=True, verbose_name="Application des connaissances")
    improvement_areas = models.TextField(blank=True, verbose_name="Domaines d'amélioration")
    follow_up_needed = models.BooleanField(default=False, verbose_name="Suivi nécessaire")

    # Coûts
    cost_covered_by_company = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                  verbose_name="Coût pris en charge par l'entreprise")
    personal_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                verbose_name="Contribution personnelle")

    # Suivi post-formation
    follow_up_date = models.DateField(null=True, blank=True, verbose_name="Date de suivi")
    follow_up_notes = models.TextField(blank=True, verbose_name="Notes de suivi")

    class Meta:
        verbose_name = "Participation à la formation"
        verbose_name_plural = "Participations aux formations"
        unique_together = ['employee', 'training']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.training.title}"

    @property
    def improvement_percentage(self):
        if self.pre_training_score and self.post_training_score:
            return self.post_training_score - self.pre_training_score
        return None


class Document(models.Model):
    """Modèle pour les documents des employés"""
    DOCUMENT_TYPES = [
        ('contract', 'Contrat de travail'),
        ('amendment', 'Avenant au contrat'),
        ('id_copy', 'Copie pièce d\'identité'),
        ('passport', 'Passeport'),
        ('diploma', 'Diplôme'),
        ('certificate', 'Certificat'),
        ('medical', 'Certificat médical'),
        ('performance', 'Évaluation de performance'),
        ('disciplinary', 'Mesure disciplinaire'),
        ('warning', 'Avertissement'),
        ('resignation', 'Lettre de démission'),
        ('termination', 'Lettre de licenciement'),
        ('reference', 'Lettre de recommandation'),
        ('training_cert', 'Certificat de formation'),
        ('bank_details', 'RIB'),
        ('insurance', 'Assurance'),
        ('other', 'Autre'),
    ]

    CONFIDENTIALITY_LEVELS = [
        ('public', 'Public'),
        ('internal', 'Interne'),
        ('confidential', 'Confidentiel'),
        ('restricted', 'Restreint'),
        ('secret', 'Secret'),
    ]

    # Informations de base
    document_id = models.CharField(max_length=20, unique=True, verbose_name="ID Document")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name="Type de document")
    title = models.CharField(max_length=200, verbose_name="Titre du document")
    description = models.TextField(blank=True, verbose_name="Description")

    # Fichier et métadonnées
    file = models.FileField(upload_to='employees/documents/', verbose_name="Fichier")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taille du fichier (bytes)")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="Type de fichier")

    # Dates importantes
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    document_date = models.DateField(null=True, blank=True, verbose_name="Date du document")
    effective_date = models.DateField(null=True, blank=True, verbose_name="Date d'entrée en vigueur")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date d'expiration")

    # Sécurité et accès
    confidentiality_level = models.CharField(max_length=20, choices=CONFIDENTIALITY_LEVELS,
                                             default='internal', verbose_name="Niveau de confidentialité")
    is_original = models.BooleanField(default=True, verbose_name="Document original")
    requires_signature = models.BooleanField(default=False, verbose_name="Signature requise")
    is_signed = models.BooleanField(default=False, verbose_name="Signé")

    # Versioning
    version = models.CharField(max_length=10, default='1.0', verbose_name="Version")
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Version précédente")

    # Suivi et validation
    uploaded_by = models.CharField(max_length=100, blank=True, verbose_name="Uploadé par")
    validated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='validated_documents', verbose_name="Validé par")
    validation_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    # Notifications
    notify_before_expiry = models.BooleanField(default=False, verbose_name="Notifier avant expiration")
    notification_days = models.PositiveIntegerField(default=30, verbose_name="Jours avant notification")

    # Tags et catégorisation
    tags = models.CharField(max_length=500, blank=True, verbose_name="Tags (séparés par des virgules)")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.title}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    @property
    def expires_soon(self):
        if self.expiry_date and self.notify_before_expiry:
            return (self.expiry_date - date.today()).days <= self.notification_days
        return False

    def save(self, *args, **kwargs):
        # Génération automatique de l'ID document
        if not self.document_id:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.document_id = f"DOC-{self.employee.employee_id}-{timestamp}"

        # Extraction des métadonnées du fichier
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].upper() if '.' in self.file.name else 'Unknown'

        super().save(*args, **kwargs)


class Disciplinary(models.Model):
    """Modèle pour les mesures disciplinaires"""
    DISCIPLINARY_TYPES = [
        ('verbal_warning', 'Avertissement verbal'),
        ('written_warning', 'Avertissement écrit'),
        ('final_warning', 'Avertissement final'),
        ('suspension', 'Suspension'),
        ('demotion', 'Rétrogradation'),
        ('salary_reduction', 'Réduction de salaire'),
        ('termination', 'Licenciement'),
        ('dismissal', 'Licenciement pour faute grave'),
    ]

    SEVERITY_LEVELS = [
        ('minor', 'Mineur'),
        ('moderate', 'Modéré'),
        ('serious', 'Grave'),
        ('severe', 'Très grave'),
        ('critical', 'Critique'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('completed', 'Terminé'),
        ('appealed', 'Contesté'),
        ('overturned', 'Annulé'),
    ]

    # Informations de base
    disciplinary_id = models.CharField(max_length=20, unique=True, verbose_name="ID Mesure")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    disciplinary_type = models.CharField(max_length=20, choices=DISCIPLINARY_TYPES, verbose_name="Type de mesure")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, verbose_name="Gravité")

    # Incident
    incident_date = models.DateField(verbose_name="Date de l'incident")
    incident_description = models.TextField(verbose_name="Description de l'incident")
    incident_location = models.CharField(max_length=200, blank=True, verbose_name="Lieu de l'incident")
    witnesses = models.TextField(blank=True, verbose_name="Témoins")

    # Mesure disciplinaire
    action_date = models.DateField(verbose_name="Date de la mesure")
    action_description = models.TextField(verbose_name="Description de la mesure")
    duration_days = models.PositiveIntegerField(null=True, blank=True, verbose_name="Durée en jours")
    effective_date = models.DateField(verbose_name="Date d'entrée en vigueur")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")

    # Responsables
    issued_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                  related_name='issued_disciplinaries', verbose_name="Émis par")
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                    related_name='approved_disciplinaries', verbose_name="Approuvé par")

    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")

    # Réponse de l'employé
    employee_response = models.TextField(blank=True, verbose_name="Réponse de l'employé")
    employee_acknowledgment = models.BooleanField(default=False, verbose_name="Accusé de réception employé")
    acknowledgment_date = models.DateField(null=True, blank=True, verbose_name="Date d'accusé de réception")

    # Appel et contestation
    appeal_submitted = models.BooleanField(default=False, verbose_name="Appel soumis")
    appeal_date = models.DateField(null=True, blank=True, verbose_name="Date d'appel")
    appeal_reason = models.TextField(blank=True, verbose_name="Motif d'appel")
    appeal_outcome = models.TextField(blank=True, verbose_name="Résultat de l'appel")

    # Documents et preuves
    supporting_documents = models.FileField(upload_to='disciplinary/', blank=True, null=True,
                                            verbose_name="Documents justificatifs")

    # Notes et commentaires
    notes = models.TextField(blank=True, verbose_name="Notes")
    hr_comments = models.TextField(blank=True, verbose_name="Commentaires RH")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mesure disciplinaire"
        verbose_name_plural = "Mesures disciplinaires"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_disciplinary_type_display()} ({self.incident_date})"

    @property
    def is_active(self):
        if self.end_date:
            return date.today() <= self.end_date
        return self.status == 'active'


class Recruitment(models.Model):
    """Modèle pour le processus de recrutement"""
    JOB_TYPES = [
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contract', 'Contractuel'),
        ('internship', 'Stage'),
        ('temporary', 'Temporaire'),
        ('freelance', 'Freelance'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('open', 'Ouvert'),
        ('closed', 'Fermé'),
        ('on_hold', 'En attente'),
        ('filled', 'Pourvu'),
        ('cancelled', 'Annulé'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevée'),
        ('urgent', 'Urgent'),
    ]

    # Informations de base
    job_id = models.CharField(max_length=20, unique=True, verbose_name="ID Poste")
    title = models.CharField(max_length=200, verbose_name="Titre du poste")
    department = models.CharField(max_length=20, choices=Employee.DEPARTMENT_CHOICES, verbose_name="Département")
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, verbose_name="Type d'emploi")

    # Description du poste
    job_description = models.TextField(verbose_name="Description du poste")
    responsibilities = models.TextField(verbose_name="Responsabilités")
    requirements = models.TextField(verbose_name="Exigences")
    qualifications = models.TextField(verbose_name="Qualifications")
    skills_required = models.TextField(verbose_name="Compétences requises")
    experience_required = models.CharField(max_length=100, verbose_name="Expérience requise")

    # Conditions d'emploi
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Salaire minimum")
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     verbose_name="Salaire maximum")
    benefits = models.TextField(blank=True, verbose_name="Avantages")
    work_location = models.CharField(max_length=200, verbose_name="Lieu de travail")
    remote_work_allowed = models.BooleanField(default=False, verbose_name="Télétravail autorisé")

    # Processus de recrutement
    hiring_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                       related_name='managed_recruitments', verbose_name="Responsable recrutement")
    recruiter = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='handled_recruitments', verbose_name="Recruteur")

    # Dates importantes
    posting_date = models.DateField(verbose_name="Date de publication")
    application_deadline = models.DateField(verbose_name="Date limite de candidature")
    target_start_date = models.DateField(null=True, blank=True, verbose_name="Date de prise de poste souhaitée")

    # Statut et priorité
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal', verbose_name="Priorité")

    # Métriques
    positions_available = models.PositiveIntegerField(default=1, verbose_name="Postes disponibles")
    positions_filled = models.PositiveIntegerField(default=0, verbose_name="Postes pourvus")

    # Budget et approbation
    budget_approved = models.BooleanField(default=False, verbose_name="Budget approuvé")
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_recruitments', verbose_name="Approuvé par")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Date d'approbation")

    # Notes
    internal_notes = models.TextField(blank=True, verbose_name="Notes internes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recrutement"
        verbose_name_plural = "Recrutements"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_id} - {self.title}"

    @property
    def applications_count(self):
        return self.applications.count()

    @property
    def is_active(self):
        return self.status == 'open' and date.today() <= self.application_deadline


class JobApplication(models.Model):
    """Modèle pour les candidatures"""
    APPLICATION_STATUS = [
        ('submitted', 'Soumise'),
        ('under_review', 'En cours d\'examen'),
        ('shortlisted', 'Présélectionnée'),
        ('interview_scheduled', 'Entretien programmé'),
        ('interviewed', 'Entretien passé'),
        ('second_interview', 'Deuxième entretien'),
        ('reference_check', 'Vérification des références'),
        ('offer_made', 'Offre faite'),
        ('offer_accepted', 'Offre acceptée'),
        ('offer_declined', 'Offre refusée'),
        ('hired', 'Embauché'),
        ('rejected', 'Rejeté'),
        ('withdrawn', 'Retirée'),
    ]

    # Informations de base
    application_id = models.CharField(max_length=20, unique=True, verbose_name="ID Candidature")
    job_posting = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name='applications',
                                    verbose_name="Offre d'emploi")

    # Informations du candidat
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    address = models.TextField(verbose_name="Adresse")

    # Documents
    resume = models.FileField(upload_to='applications/resumes/', verbose_name="CV")
    cover_letter = models.FileField(upload_to='applications/cover_letters/', blank=True, null=True,
                                    verbose_name="Lettre de motivation")
    portfolio = models.URLField(blank=True, verbose_name="Portfolio (URL)")

    # Expérience et formation
    current_position = models.CharField(max_length=200, blank=True, verbose_name="Poste actuel")
    current_company = models.CharField(max_length=200, blank=True, verbose_name="Entreprise actuelle")
    years_experience = models.PositiveIntegerField(verbose_name="Années d'expérience")
    education_level = models.CharField(max_length=20, choices=Employee.EDUCATION_LEVEL_CHOICES,
                                       verbose_name="Niveau d'éducation")

    # Prétentions
    salary_expectation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                             verbose_name="Prétentions salariales")
    availability_date = models.DateField(verbose_name="Date de disponibilité")
    notice_period = models.CharField(max_length=100, blank=True, verbose_name="Préavis")

    # Statut et suivi
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='submitted', verbose_name="Statut")
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de candidature")

    # Évaluation
    screening_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                                          verbose_name="Score de présélection (/10)")
    interview_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                                          verbose_name="Score d'entretien (/10)")
    overall_rating = models.IntegerField(choices=Performance.RATING_CHOICES, null=True, blank=True,
                                         verbose_name="Évaluation globale")

    # Entretiens
    interview_date = models.DateTimeField(null=True, blank=True, verbose_name="Date d'entretien")
    interviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='conducted_interviews', verbose_name="Intervieweur")
    interview_notes = models.TextField(blank=True, verbose_name="Notes d'entretien")

    # Références
    references_checked = models.BooleanField(default=False, verbose_name="Références vérifiées")
    reference_feedback = models.TextField(blank=True, verbose_name="Retour des références")

    # Décision finale
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de refus")
    feedback_to_candidate = models.TextField(blank=True, verbose_name="Retour au candidat")

    # Notes internes
    recruiter_notes = models.TextField(blank=True, verbose_name="Notes du recruteur")
    hiring_manager_notes = models.TextField(blank=True, verbose_name="Notes du responsable")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_posting.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def days_since_application(self):
        return (timezone.now().date() - self.application_date.date()).days