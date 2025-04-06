from django.db import models
from hospital.models import Doctor

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    patient_contact = models.CharField(max_length=15)
    appointment_time = models.CharField(max_length=20)
    waiting_time = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this line

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} ({self.appointment_time})"
