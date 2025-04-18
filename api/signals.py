from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
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


# change role from patient to doctor / admin will delete patient profile
@receiver(pre_save, sender=User)
def update_user_profile(sender, instance, **kwargs):
    if not instance.pk:
        return  # New user handled in post_save

    old_user = User.objects.get(pk=instance.pk)
    old_role = old_user.role
    new_role = instance.role

    if old_role != new_role:
        # Delete old profile
        if old_role == User.Role.PATIENT:
            PatientProfile.objects.filter(user=instance).delete()
        elif old_role == User.Role.DOCTOR:
            DoctorProfile.objects.filter(user=instance).delete()

        # Create new profile
        if new_role == User.Role.PATIENT:
            PatientProfile.objects.get_or_create(user=instance)
        elif new_role == User.Role.DOCTOR:
            DoctorProfile.objects.get_or_create(user=instance)
