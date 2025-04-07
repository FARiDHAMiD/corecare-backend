from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save, post_delete
from .models import DoctorProfile, User, PatientProfile

from django.core.files.storage import default_storage

# Auto delete images 
@receiver(post_delete, sender=DoctorProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Delete image file from storage when DoctorProfile is deleted."""
    if instance.image:
        if default_storage.exists(instance.image.name):
            default_storage.delete(instance.image.name)

# auto create pateint profile
@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created:  # Ensure it only runs on creation
        PatientProfile.objects.create(user=instance)
