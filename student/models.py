from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=100)
    symbolNo = models.PositiveIntegerField(unique=True)
    batch = models.PositiveIntegerField()
    faculty = models.CharField(max_length=88)
    address = models.CharField(max_length=255)
    phoneNo = models.PositiveIntegerField(max_length=11)
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id , "-", self.name

