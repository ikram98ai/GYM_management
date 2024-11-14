from django.db import models
from datetime import date
from django.utils import timezone
from datetime import timedelta

class Member(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    name = models.CharField(max_length=100)
    birthdate = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15,unique=True)
    address = models.TextField()
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    join_date = models.DateField(auto_now_add=True)

    def age(self):
        return (date.today() - self.birthdate).days // 365

    def __str__(self):
        return f"{self.name} ({self.contact_number})"

class HealthLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,related_name='healthlog')
    date_logged = models.DateField(auto_now_add=True)
    weight = models.FloatField()
    height = models.FloatField()

    def bmi(self):
        return round(self.weight / ((self.height / 100) ** 2), 2)



class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)  # Automatically set current datetime
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Paid')

    def save(self, *args, **kwargs):
        # Ensure date_paid is set
        if not self.date_paid:
            self.date_paid = timezone.now()

        # If due_date is not set, calculate it as 30 days from date_paid
        if not self.due_date:
            self.due_date = self.date_paid.date() + timedelta(days=30)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.name} - {self.status}"

    @property
    def update_status(self):
        # Automatically mark status as 'Unpaid' if due_date has passed
        if self.due_date < timezone.now().date():
            self.status = 'Unpaid'
            self.save()

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(blank=True, null=True)
