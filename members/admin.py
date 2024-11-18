from django.contrib import admin
from .models import Member, Payment, HealthLog, Attendance
from django.utils.html import format_html
from datetime import timedelta
from django.utils import timezone

# Inline for HealthLog
class HealthLogInline(admin.TabularInline):
    """
    Inline model for displaying HealthLog details on the Member admin page.
    Allows adding and editing health logs directly from the Member page.
    """
    model = HealthLog
    extra = 1  # Number of empty forms to display for adding new records
    fields = ('weight', 'height', 'date_logged')
    readonly_fields = ('date_logged',)
    can_delete = True

# Inline for Attendance
class AttendanceInline(admin.TabularInline):
    """
    Inline model for displaying Attendance details on the Member admin page.
    Allows adding and editing attendance records directly from the Member page.
    """
    model = Attendance
    extra = 1  # Number of empty forms to display for adding new records
    fields = ('check_in', 'check_out')
    readonly_fields = ('check_in', 'check_out')
    can_delete = True


class PaymentInline(admin.TabularInline):
    """
    Inline model for displaying Payment details on the Member admin page.
    Allows adding and editing payments directly from the Member page.
    """
    model = Payment
    extra = 1  # Number of empty forms to display for adding new records
    fields = ('amount', 'date_paid', 'due_date', 'status')
    readonly_fields = ('date_paid', 'due_date', 'status')
    can_delete = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Update payment status based on due_date
        for payment in qs:
            if payment.due_date and payment.due_date < timezone.now().date():
                payment.status = 'Unpaid'
                payment.save()
        return qs


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """
    Admin interface for managing gym members.
    """
    list_display = ('name', 'contact_number', 'join_date', 'profile_photo_thumbnail', 'active_membership')
    search_fields = ('name', 'contact_number')
    list_filter = ('join_date',)
    inlines = [PaymentInline, HealthLogInline, AttendanceInline]
    readonly_fields = ('profile_photo_thumbnail',)

    def profile_photo_thumbnail(self, obj):
        """
        Display a small profile picture thumbnail in the admin panel.
        """
        if obj.profile_photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;"/>', obj.profile_photo.url)
        return "No Photo"

    profile_photo_thumbnail.short_description = 'Profile Photo'

    def active_membership(self, obj):
        """
        Show active membership status based on the latest payment.
        """
        latest_payment = Payment.objects.filter(member=obj).order_by('-due_date').first()
        if latest_payment and latest_payment.due_date >= timezone.now().date():
            return format_html('<span style="color:green;">Active</span>')
        return format_html('<span style="color:red;">Expired</span>')

    active_membership.short_description = 'Membership Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing gym member payments.
    """
    list_display = ('member', 'amount', 'date_paid', 'due_date', 'status')
    list_filter = ('status', 'date_paid', 'due_date')
    search_fields = ('member__name',)
    readonly_fields = ('date_paid', 'due_date', 'status')
    actions = ['mark_all_as_unpaid']

    def save_model(self, request, obj, form, change):
        """
        Automatically set due_date and status on save.
        """
        if not obj.date_paid:
            obj.date_paid = timezone.now()
        if not obj.due_date:
            obj.due_date = obj.date_paid.date() + timedelta(days=30)

        # Automatically set status based on due_date
        if obj.due_date < timezone.now().date():
            obj.status = 'Unpaid'
        else:
            obj.status = 'Paid'

        super().save_model(request, obj, form, change)

    def mark_all_as_unpaid(self, request, queryset):
        """
        Custom action to mark selected payments as 'Unpaid'.
        """
        updated = queryset.update(status='Unpaid')
        self.message_user(request, f"{updated} payment(s) marked as Unpaid.")

    mark_all_as_unpaid.short_description = 'Mark selected payments as Unpaid'


@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    """
    Admin interface for managing health logs of gym members.
    """
    list_display = ('member', 'weight', 'height', 'bmi', 'date_logged')
    list_filter = ('date_logged',)
    search_fields = ('member__name',)
    readonly_fields = ('date_logged',)

    def save_model(self, request, obj, form, change):
        """
        Automatically calculate BMI before saving the health log.
        """
        if obj.weight and obj.height:
            obj.bmi = obj.weight / (obj.height ** 2)
        super().save_model(request, obj, form, change)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing attendance logs of gym members.
    """
    list_display = ('member', 'check_in', 'check_out')
    list_filter = ('check_in',)
    search_fields = ('member__name',)
    readonly_fields = ('check_in', 'check_out')

    def save_model(self, request, obj, form, change):
        """
        Automatically set check_out if not set when a member checks out.
        """
        if obj.check_in and not obj.check_out:
            obj.check_out = timezone.now()  # Mark the checkout time as current datetime
        super().save_model(request, obj, form, change)
