from django.db import models
from core.storage_backend import mediaStoarge

def media_storage_path (instance, filename):
    return f'students/{instance.symbolNo}/{filename}'

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    symbolNo = models.PositiveIntegerField(unique=True)
    batch = models.PositiveIntegerField()
    faculty = models.CharField(max_length=88)
    address = models.CharField(max_length=255)
    # Phone numbers are better stored as CharField to preserve leading zeros and allow validation.
    phoneNo = models.CharField(max_length=11)
    isActive = models.BooleanField(default=True)
    profile = models.ImageField(
        upload_to=media_storage_path,
        storage=mediaStoarge,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return a readable string representation of the student.
        return f"{self.id} - {self.name}"

