from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import (
    Employee, Intern, Department, LeaveRequest, Attendance, Payroll,
    Performance, Training, TrainingParticipation, Document, Disciplinary,
    Recruitment, JobApplication
)


# Configuration de l'admin site pour la section RH
class HRAdminSite(admin.AdminSite):
    site_header = "🏢 Système de Gestion RH Complet - MonMarché"
    site_title = "RH Admin"
    index_title = "Tableau de bord RH - Vue d'ensemble"

    def index(self, request, extra_context=None):
        """Tableau de bord avec statistiques complètes"""
        extra_context = extra_context or {}

        # Statistiques générales
        total_employees = Employee.objects.filter(status='active').count()
        total_interns = Intern.objects.filter(status='active').count()
        total_departments = Department.objects.count()
        pending_leaves = LeaveRequest.objects.filter(status='pending').count()

        # Statistiques par département
        dept_stats = Employee.objects.filter(status='active').values('department').annotate(
            count=Count('id')
        ).order_by('-count')

        # Statistiques de formation
        ongoing_trainings = Training.objects.filter(status='ongoing').count()
        completed_trainings_this_month = Training.objects.filter(
            status='completed',
            end_date__month=date.today().month,
            end_date__year=date.today().year
        ).count()

        # Statistiques de recrutement
        open_positions = Recruitment.objects.filter(status='open').count()
        pending_applications = JobApplication.objects.filter(status='under_review').count()

        # Anniversaires de travail ce mois
        current_month = date.today().month
        work_anniversaries = Employee.objects.filter(
            hire_date__month=current_month,
            status='active'
        ).count()

        # Contrats expirant bientôt
        next_month = date.today() + timedelta(days=30)
        expiring_contracts = Employee.objects.filter(
            contract_end_date__lte=next_month,
            contract_end_date__gte=date.today(),
            status='active'
        ).count()

        # Documents expirant bientôt
        expiring_documents = Document.objects.filter(
            expiry_date__lte=next_month,
            expiry_date__gte=date.today()
        ).count()

        # Évaluations en retard
        overdue_evaluations = Employee.objects.filter(
            status='active'
        ).exclude(
            performance__period_end__gte=date.today() - timedelta(days=365)
        ).count()

        extra_context.update({
            'total_employees': total_employees,
            'total_interns': total_interns,
            'total_departments': total_departments,
            'pending_leaves': pending_leaves,
            'dept_stats': dept_stats,
            'ongoing_trainings': ongoing_trainings,
            'completed_trainings_this_month': completed_trainings_this_month,
            'open_positions': open_positions,
            'pending_applications': pending_applications,
            'work_anniversaries': work_anniversaries,
            'expiring_contracts': expiring_contracts,
            'expiring_documents': expiring_documents,
            'overdue_evaluations': overdue_evaluations,
        })

        return super().index(request, extra_context)


hr_admin_site = HRAdminSite(name='hr_admin')


@admin.register(Employee, site=hr_admin_site)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'email', 'department',
        'position', 'status_display', 'hire_date', 'salary_display',
        'age_display', 'contract_status'
    ]
    list_filter = [
        'department', 'status', 'contract_type', 'gender', 'hire_date',
        'education_level', 'marital_status'
    ]
    search_fields = [
        'employee_id', 'first_name', 'last_name', 'middle_name', 'email',
        'phone', 'position', 'id_number', 'skills'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'age_display', 'years_of_service_display',
        'contract_expires_soon_display', 'is_on_probation_display'
    ]
    list_per_page = 25
    date_hierarchy = 'hire_date'

    fieldsets = (
        ('🆔 Informations de base', {
            'fields': (
                ('employee_id', 'status'),
                ('first_name', 'middle_name', 'last_name'),
                ('maiden_name',),
                ('email', 'personal_email'),
                ('phone', 'mobile_phone', 'whatsapp'),
                'photo'
            )
        }),
        ('👤 Informations personnelles', {
            'fields': (
                ('date_of_birth', 'place_of_birth', 'age_display'),
                ('gender', 'marital_status', 'nationality'),
                ('id_number', 'passport_number', 'social_security_number'),
            ),
            'classes': ('collapse',)
        }),
        ('📍 Adresses', {
            'fields': (
                'address', ('city', 'postal_code', 'country'),
                'secondary_address', ('secondary_city', 'secondary_postal_code'),
            ),
            'classes': ('collapse',)
        }),
        ('💼 Informations professionnelles', {
            'fields': (
                ('department', 'position'),
                'job_description',
                ('hire_date', 'probation_end_date', 'years_of_service_display'),
                ('contract_type', 'contract_start_date', 'contract_end_date'),
                ('manager',),
                ('work_schedule', 'weekly_hours'),
                'is_on_probation_display',
                'contract_expires_soon_display'
            )
        }),
        ('💰 Rémunération', {
            'fields': (
                ('salary', 'hourly_rate', 'overtime_rate'),
            )
        }),
        ('🏦 Informations bancaires', {
            'fields': (
                ('bank_name', 'bank_account'),
                ('iban', 'swift_code')
            ),
            'classes': ('collapse',)
        }),
        ('🎓 Éducation et compétences', {
            'fields': (
                ('education_level', 'university'),
                ('degree', 'graduation_year'),
                'skills', 'languages', 'certifications'
            ),
            'classes': ('collapse',)
        }),
        ('🚨 Contacts d\'urgence', {
            'fields': (
                ('emergency_contact_1_name', 'emergency_contact_1_phone', 'emergency_contact_1_relationship'),
                ('emergency_contact_2_name', 'emergency_contact_2_phone', 'emergency_contact_2_relationship'),
            ),
            'classes': ('collapse',)
        }),
        ('🏥 Informations médicales', {
            'fields': (
                ('blood_type', 'medical_insurance_number'),
                'allergies', 'medical_conditions'
            ),
            'classes': ('collapse',)
        }),
        ('⚙️ Préférences et divers', {
            'fields': (
                'preferred_communication',
                'signature',
                'notes'
            ),
            'classes': ('collapse',)
        }),
        ('📝 Fin de contrat', {
            'fields': (
                ('termination_date', 'termination_reason'),
            ),
            'classes': ('collapse',)
        }),
        ('🔍 Suivi et audit', {
            'fields': (
                ('created_by', 'last_modified_by'),
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Nom complet"
    get_full_name.admin_order_field = 'first_name'

    def status_display(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'red',
            'on_leave': 'orange',
            'terminated': 'red',
            'retired': 'gray',
            'suspended': 'red',
            'probation': 'blue'
        }
        icons = {
            'active': '✅',
            'inactive': '❌',
            'on_leave': '🏖️',
            'terminated': '🚫',
            'retired': '👴',
            'suspended': '⏸️',
            'probation': '🔄'
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.status, 'black'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )

    status_display.short_description = "Statut"

    def salary_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{:,.0f} F CFA</span>',
            obj.salary
        )

    salary_display.short_description = "Salaire"
    salary_display.admin_order_field = 'salary'

    def age_display(self, obj):
        return f"{obj.age} ans"

    age_display.short_description = "Âge"

    def years_of_service_display(self, obj):
        years = obj.years_of_service
        if years == 0:
            return "Moins d'un an"
        return f"{years} an{'s' if years > 1 else ''}"

    years_of_service_display.short_description = "Ancienneté"

    def contract_expires_soon_display(self, obj):
        if obj.contract_expires_soon:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Expire bientôt</span>')
        return format_html('<span style="color: green;">✅ OK</span>')

    contract_expires_soon_display.short_description = "Contrat"

    def is_on_probation_display(self, obj):
        if obj.is_on_probation:
            return format_html('<span style="color: orange;">🔄 En période d\'essai</span>')
        return format_html('<span style="color: green;">✅ Confirmé</span>')

    is_on_probation_display.short_description = "Période d'essai"

    def contract_status(self, obj):
        if obj.contract_end_date:
            days_left = (obj.contract_end_date - date.today()).days
            if days_left <= 0:
                return format_html('<span style="color: red;">❌ Expiré</span>')
            elif days_left <= 30:
                return format_html('<span style="color: orange;">⚠️ {} jours</span>', days_left)
            else:
                return format_html('<span style="color: green;">✅ {} jours</span>', days_left)
        return format_html('<span style="color: blue;">♾️ CDI</span>')

    contract_status.short_description = "Contrat"

    actions = ['activate_employees', 'deactivate_employees', 'confirm_probation', 'generate_id_cards']

    def activate_employees(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} employé(s) activé(s).')

    activate_employees.short_description = "✅ Activer les employés sélectionnés"

    def deactivate_employees(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} employé(s) désactivé(s).')

    deactivate_employees.short_description = "❌ Désactiver les employés sélectionnés"

    def confirm_probation(self, request, queryset):
        updated = queryset.filter(status='probation').update(status='active')
        self.message_user(request, f'{updated} employé(s) confirmé(s) après période d\'essai.')

    confirm_probation.short_description = "✅ Confirmer après période d'essai"


@admin.register(Intern, site=hr_admin_site)
class InternAdmin(admin.ModelAdmin):
    list_display = [
        'intern_id', 'get_full_name', 'email', 'school', 'department',
        'supervisor', 'start_date', 'end_date', 'status_display', 'progress_display'
    ]
    list_filter = ['internship_type', 'status', 'department', 'is_paid', 'start_date']
    search_fields = ['intern_id', 'first_name', 'last_name', 'email', 'school', 'field_of_study']
    readonly_fields = ['created_at', 'updated_at', 'age_display', 'days_remaining_display',
                       'progress_percentage_display']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('🆔 Informations de base', {
            'fields': (
                ('intern_id', 'status'),
                ('first_name', 'last_name'),
                ('email', 'phone'),
                'age_display'
            )
        }),
        ('📍 Adresse', {
            'fields': (
                'address', ('city', 'postal_code')
            )
        }),
        ('🎓 Informations académiques', {
            'fields': (
                ('school', 'field_of_study'),
                ('academic_level', 'academic_year')
            )
        }),
        ('💼 Informations de stage', {
            'fields': (
                ('internship_type', 'department'),
                'supervisor',
                ('start_date', 'end_date', 'duration_weeks'),
                'days_remaining_display',
                'progress_percentage_display',
                'objectives',
                'tasks_assigned'
            )
        }),
        ('💰 Rémunération', {
            'fields': (
                ('is_paid', 'monthly_allowance')
            )
        }),
        ('🚨 Contact d\'urgence', {
            'fields': (
                ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
            )
        }),
        ('📋 Suivi et évaluation', {
            'fields': (
                ('convention_signed', 'final_report_submitted'),
                'final_grade'
            )
        }),
        ('📝 Suivi', {
            'fields': (
                ('created_by', 'created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    get_full_name.short_description = "Nom complet"

    def status_display(self, obj):
        colors = {
            'active': 'green',
            'completed': 'blue',
            'terminated': 'red',
            'extended': 'orange'
        }
        icons = {
            'active': '🔄',
            'completed': '✅',
            'terminated': '❌',
            'extended': '⏰'
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.status, 'black'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )

    status_display.short_description = "Statut"

    def progress_display(self, obj):
        progress = obj.progress_percentage
        color = 'green' if progress >= 75 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 10px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 10px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{:.0f}%</div></div>',
            progress, color, progress
        )

    progress_display.short_description = "Progression"

    def age_display(self, obj):
        return f"{obj.age} ans"

    age_display.short_description = "Âge"

    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if days > 0:
            return format_html('<span style="color: blue;">{} jours</span>', days)
        elif days == 0:
            return format_html('<span style="color: orange;">Dernier jour</span>')
        else:
            return format_html('<span style="color: red;">Terminé</span>')

    days_remaining_display.short_description = "Jours restants"

    def progress_percentage_display(self, obj):
        return f"{obj.progress_percentage:.1f}%"

    progress_percentage_display.short_description = "Progression"


@admin.register(Department, site=hr_admin_site)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'manager', 'assistant_manager',
        'employee_count_display', 'intern_count_display',
        'budget_display', 'location'
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'employee_count_display', 'intern_count_display']

    fieldsets = (
        ('🏢 Informations de base', {
            'fields': (
                ('code', 'name'),
                'description',
                ('manager', 'assistant_manager')
            )
        }),
        ('📍 Localisation et contact', {
            'fields': (
                'location',
                ('phone', 'email')
            )
        }),
        ('💰 Budget et objectifs', {
            'fields': (
                'budget',
                'objectives',
                'kpis'
            ),
            'classes': ('collapse',)
        }),
        ('📊 Statistiques', {
            'fields': (
                'employee_count_display',
                'intern_count_display',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def employee_count_display(self, obj):
        count = obj.employee_count
        color = 'green' if count > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">👥 {} employé(s)</span>',
            color, count
        )

    employee_count_display.short_description = "Effectif employés"

    def intern_count_display(self, obj):
        count = obj.intern_count
        color = 'blue' if count > 0 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">🎓 {} stagiaire(s)</span>',
            color, count
        )

    intern_count_display.short_description = "Effectif stagiaires"

    def budget_display(self, obj):
        if obj.budget:
            return format_html(
                '<span style="color: blue; font-weight: bold;">💰 {:,.0f} F CFA</span>',
                obj.budget
            )
        return format_html('<span style="color: gray;">Non défini</span>')

    budget_display.short_description = "Budget"


@admin.register(LeaveRequest, site=hr_admin_site)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'leave_type', 'start_date', 'end_date',
        'days_requested', 'status_display', 'priority_display',
        'approved_by', 'created_at'
    ]
    list_filter = [
        'leave_type', 'status', 'priority', 'start_date',
        'created_at', 'employee__department'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'employee__employee_id', 'reason'
    ]
    readonly_fields = ['created_at', 'updated_at', 'request_id', 'days_until_start_display']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('📋 Demande de congé', {
            'fields': (
                'request_id',
                ('employee', 'leave_type', 'priority'),
                ('start_date', 'end_date', 'days_requested'),
                ('half_day_start', 'half_day_end'),
                'reason',
                'supporting_documents',
                'days_until_start_display'
            )
        }),
        ('👥 Remplacement', {
            'fields': (
                'replacement_employee',
                'handover_notes'
            ),
            'classes': ('collapse',)
        }),
        ('✅ Approbation', {
            'fields': (
                ('status', 'approved_by', 'approved_date'),
                'rejection_reason',
                'comments',
                'hr_comments'
            )
        }),
        ('📅 Suivi', {
            'fields': (
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'gray',
            'in_progress': 'blue',
            'completed': 'darkgreen'
        }
        icons = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌',
            'cancelled': '🚫',
            'in_progress': '🔄',
            'completed': '✅'
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.status, 'black'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )

    status_display.short_description = "Statut"

    def priority_display(self, obj):
        colors = {
            'low': 'green',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )

    priority_display.short_description = "Priorité"

    def days_until_start_display(self, obj):
        days = obj.days_until_start
        if days > 0:
            return format_html('<span style="color: blue;">Dans {} jours</span>', days)
        elif days == 0:
            return format_html('<span style="color: orange;">Aujourd\'hui</span>')
        else:
            return format_html('<span style="color: gray;">Commencé</span>')

    days_until_start_display.short_description = "Début"

    actions = ['approve_requests', 'reject_requests', 'mark_in_progress']

    def approve_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_date=timezone.now()
        )
        self.message_user(request, f'{updated} demande(s) approuvée(s).')

    approve_requests.short_description = "✅ Approuver les demandes sélectionnées"

    def reject_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} demande(s) rejetée(s).')

    reject_requests.short_description = "❌ Rejeter les demandes sélectionnées"

    def mark_in_progress(self, request, queryset):
        updated = queryset.filter(status='approved').update(status='in_progress')
        self.message_user(request, f'{updated} demande(s) marquée(s) en cours.')

    mark_in_progress.short_description = "🔄 Marquer en cours"


# Enregistrement des autres modèles avec des admins simplifiés pour l'espace
@admin.register(Attendance, site=hr_admin_site)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'total_hours', 'status_display']
    list_filter = ['status', 'date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'

    def status_display(self, obj):
        colors = {
            'present': 'green', 'absent': 'red', 'late': 'orange',
            'half_day': 'blue', 'on_leave': 'purple', 'sick': 'red',
            'remote': 'teal', 'business_trip': 'navy', 'training': 'indigo'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'), obj.get_status_display()
        )

    status_display.short_description = "Statut"


@admin.register(Payroll, site=hr_admin_site)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month_year', 'base_salary_display', 'gross_salary_display', 'net_salary_display',
                    'status_display']
    list_filter = ['year', 'month', 'status', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'payroll_id']
    readonly_fields = ['payroll_id', 'gross_salary', 'total_allowances', 'total_deductions', 'net_salary', 'created_at']

    def month_year(self, obj):
        return f"{obj.month:02d}/{obj.year}"

    month_year.short_description = "Période"

    def base_salary_display(self, obj):
        return format_html('<span style="color: blue;">{:,.0f} F</span>', obj.base_salary)

    base_salary_display.short_description = "Salaire de base"

    def gross_salary_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">{:,.0f} F</span>', obj.gross_salary)

    gross_salary_display.short_description = "Salaire brut"

    def net_salary_display(self, obj):
        return format_html('<span style="color: darkgreen; font-weight: bold;">{:,.0f} F</span>', obj.net_salary)

    net_salary_display.short_description = "Salaire net"

    def status_display(self, obj):
        colors = {'draft': 'gray', 'calculated': 'blue', 'approved': 'green', 'paid': 'darkgreen', 'cancelled': 'red'}
        return format_html('<span style="color: {};">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"


@admin.register(Performance, site=hr_admin_site)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluator', 'evaluation_type', 'period_start', 'period_end', 'overall_rating_display',
                    'average_rating_display']
    list_filter = ['evaluation_type', 'overall_rating', 'period_start', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name']
    readonly_fields = ['evaluation_id', 'average_rating_display', 'created_at']

    def overall_rating_display(self, obj):
        colors = {1: 'red', 2: 'orange', 3: 'blue', 4: 'green', 5: 'darkgreen'}
        stars = '⭐' * obj.overall_rating
        return format_html('<span style="color: {};">{} ({})</span>', colors.get(obj.overall_rating, 'black'), stars,
                           obj.get_overall_rating_display())

    overall_rating_display.short_description = "Note globale"

    def average_rating_display(self, obj):
        return format_html('<span style="font-weight: bold;">{:.1f}/5</span>', obj.average_rating)

    average_rating_display.short_description = "Moyenne"


@admin.register(Training, site=hr_admin_site)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['title', 'training_type', 'category', 'trainer', 'start_date', 'participants_display',
                    'cost_display', 'status_display']
    list_filter = ['training_type', 'category', 'status', 'start_date']
    search_fields = ['title', 'trainer', 'description']
    readonly_fields = ['training_id', 'current_participants_display', 'available_spots_display', 'created_at']

    def participants_display(self, obj):
        current = obj.current_participants
        maximum = obj.max_participants
        percentage = (current / maximum * 100) if maximum > 0 else 0
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html('<span style="color: {};">{}/{} ({:.0f}%)</span>', color, current, maximum, percentage)

    participants_display.short_description = "Participants"

    def cost_display(self, obj):
        return format_html('<span style="color: blue;">{:,.0f} F CFA</span>', obj.total_budget)

    cost_display.short_description = "Budget total"

    def status_display(self, obj):
        colors = {'planned': 'blue', 'registration_open': 'green', 'ongoing': 'orange', 'completed': 'darkgreen',
                  'cancelled': 'red'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"

    def current_participants_display(self, obj):
        return obj.current_participants

    current_participants_display.short_description = "Participants actuels"

    def available_spots_display(self, obj):
        return obj.available_spots

    available_spots_display.short_description = "Places disponibles"


@admin.register(TrainingParticipation, site=hr_admin_site)
class TrainingParticipationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training', 'status_display', 'final_score', 'certificate_issued']
    list_filter = ['status', 'certificate_issued', 'training__status']
    search_fields = ['employee__first_name', 'employee__last_name', 'training__title']

    def status_display(self, obj):
        colors = {'registered': 'blue', 'confirmed': 'orange', 'attended': 'green', 'completed': 'darkgreen',
                  'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"


@admin.register(Document, site=hr_admin_site)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'title', 'upload_date', 'expiry_date', 'confidentiality_level',
                    'expires_soon_display']
    list_filter = ['document_type', 'confidentiality_level', 'upload_date', 'expiry_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'title', 'description']
    readonly_fields = ['document_id', 'upload_date', 'file_size', 'file_type', 'expires_soon_display']

    def expires_soon_display(self, obj):
        if obj.expires_soon:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Expire bientôt</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">❌ Expiré</span>')
        return format_html('<span style="color: green;">✅ OK</span>')

    expires_soon_display.short_description = "Statut expiration"


@admin.register(Disciplinary, site=hr_admin_site)
class DisciplinaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'disciplinary_type', 'severity', 'incident_date', 'status_display', 'issued_by']
    list_filter = ['disciplinary_type', 'severity', 'status', 'incident_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'incident_description']
    readonly_fields = ['disciplinary_id', 'created_at']

    def status_display(self, obj):
        colors = {'pending': 'orange', 'active': 'red', 'completed': 'green', 'appealed': 'blue', 'overturned': 'gray'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"


@admin.register(Recruitment, site=hr_admin_site)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'title', 'department', 'job_type', 'posting_date', 'application_deadline',
                    'applications_count_display', 'status_display']
    list_filter = ['job_type', 'status', 'department', 'priority', 'posting_date']
    search_fields = ['job_id', 'title', 'job_description']
    readonly_fields = ['job_id', 'applications_count_display', 'created_at']

    def applications_count_display(self, obj):
        count = obj.applications_count
        color = 'green' if count > 0 else 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{} candidature(s)</span>', color, count)

    applications_count_display.short_description = "Candidatures"

    def status_display(self, obj):
        colors = {'draft': 'gray', 'open': 'green', 'closed': 'red', 'on_hold': 'orange', 'filled': 'blue',
                  'cancelled': 'red'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"


@admin.register(JobApplication, site=hr_admin_site)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name_display', 'job_posting', 'application_date', 'status_display', 'overall_rating_display',
                    'days_since_application_display']
    list_filter = ['status', 'job_posting__department', 'application_date', 'overall_rating']
    search_fields = ['first_name', 'last_name', 'email', 'application_id']
    readonly_fields = ['application_id', 'application_date', 'full_name_display', 'days_since_application_display']

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Nom complet"

    def status_display(self, obj):
        colors = {
            'submitted': 'blue', 'under_review': 'orange', 'shortlisted': 'green',
            'interview_scheduled': 'purple', 'interviewed': 'teal', 'hired': 'darkgreen',
            'rejected': 'red', 'withdrawn': 'gray'
        }
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'),
                           obj.get_status_display())

    status_display.short_description = "Statut"

    def overall_rating_display(self, obj):
        if obj.overall_rating:
            stars = '⭐' * obj.overall_rating
            return format_html('<span>{}</span>', stars)
        return '-'

    overall_rating_display.short_description = "Évaluation"

    def days_since_application_display(self, obj):
        days = obj.days_since_application
        color = 'red' if days > 30 else 'orange' if days > 14 else 'green'
        return format_html('<span style="color: {};">{} jours</span>', color, days)

    days_since_application_display.short_description = "Ancienneté"


# Enregistrement dans l'admin principal pour accès rapide
@admin.register(Employee)
class EmployeeMainAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'status']
    list_filter = ['department', 'status']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Nom complet"


@admin.register(Intern)
class InternMainAdmin(admin.ModelAdmin):
    list_display = ['intern_id', 'get_full_name', 'department', 'status']
    list_filter = ['department', 'status']
    search_fields = ['intern_id', 'first_name', 'last_name', 'email']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    get_full_name.short_description = "Nom complet"