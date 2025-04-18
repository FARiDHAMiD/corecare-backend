import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

from django.core.files.storage import default_storage


# User Model with Role-Based Access Control
class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", _("Patient")
        DOCTOR = "DOCTOR", _("Doctor")
        ADMIN = "ADMIN", _("Admin")
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
# Doctor Profile
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    image = models.ImageField(upload_to="doctor_images/", blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="doctors", blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
            return f'{self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        # Check if the object already exists in the database
        if self.pk:
            existing = DoctorProfile.objects.get(pk=self.pk)
            if existing.image and self.image != existing.image:
                # Delete the old image if a new one is uploaded
                if default_storage.exists(existing.image.name):
                    default_storage.delete(existing.image.name)

        super().save(*args, **kwargs)

# Patient Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    height = models.FloatField(default=0)
    weight = models.FloatField(default=0)
    bmi = models.FloatField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.height and self.weight:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - Create_on {self.created_at}'


# Report Type Model
class ReportType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Lab Reports
class LabReport(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="lab_reports")
    report = models.FileField(upload_to="lab_reports/")
    report_type = models.ForeignKey(ReportType, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.patient.user.first_name} {self.patient.user.last_name} - {self.report_type.name}'    

# Appointment Model
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('canceled', 'canceled'),
        ('no-show', 'no-show'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_appointments")
    time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.patient.first_name} {self.patient.last_name} on {self.time}'

# Pre-visit Question Model
class PreVisitQuestion(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="pre_visit_questions")
    question_text = models.TextField()

    def __str__(self):
        return f'{self.department.name} - {self.question_text}'

# Pre-visit Report
class PreVisitReport(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="pre_visit_report")
    responses = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.appointment.patient.first_name} {self.appointment.patient.last_name} | {self.appointment.time} | {self.appointment.doctor.doctor_profile.department.name}'