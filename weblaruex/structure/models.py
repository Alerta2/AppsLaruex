from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Delete profile when user is deleted
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    telefono = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, null=True, blank=True)
    id_telegram = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(default='profile/default.png', upload_to='profile')

    def __str__(self):
        return f'{self.user.username} Profile' #show how we want it to be displayed

