from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(
        upload_to='profiles/',
        default='profiles/default.png',
        blank=True
    )

    def __str__(self):
        return self.full_name

