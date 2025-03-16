from django.db import models

# Create your models here.
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="doctor_photos/")
    experience = models.PositiveIntegerField()
    specialization = models.CharField(max_length=100)
    available_days = models.CharField(max_length=200)  # Stores selected days as comma-separated values
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.specialization}"