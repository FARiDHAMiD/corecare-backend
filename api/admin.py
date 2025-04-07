from django.contrib import admin
# from import_export.admin import ImportExportModelAdmin
# from import_export import resources
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import *

# from django.contrib.auth.models import User  # Default Django User model
from django.core.cache import cache
from .models import User as CustomUser  # Your custom User model


# Custom User Appearence in admin panel
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name'):
            raise forms.ValidationError("First name is required.")
        if not cleaned_data.get('last_name'):
            raise forms.ValidationError("Last name is required.")
        if not cleaned_data.get('email'):
            raise forms.ValidationError("Email is required.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        



class CustomUserAdmin(UserAdmin):

    form = CustomUserForm

    # Modify the "Add User" form to include first name, last name, and email initially
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "dob", "email", "phone",)}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    list_display = ("username", "email", "role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)

    # Optional: Make password readonly in the admin panel to prevent unwanted errors
    readonly_fields = ("password",)

    def save_model(self, request, obj, form, change):
        if change:
            original = User.objects.get(pk=obj.pk)
            if original.role != obj.role:
                cache.delete(f"user_token_{obj.pk}")  # Invalidate token
        
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'time', 'status']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "patient":
            kwargs["queryset"] = User.objects.filter(role=User.Role.PATIENT)
        elif db_field.name == "doctor":
            kwargs["queryset"] = User.objects.filter(role=User.Role.DOCTOR)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Department)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(PreVisitQuestion)
admin.site.register(PreVisitReport)
admin.site.register(LabReport)
admin.site.register(ReportType)

