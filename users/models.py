from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

# Create your models here.
class User(AbstractUser):
    username=None
    email=models.EmailField(_("email address"),unique=True, null=False)
    grantee=models.CharField(max_length=50,null=True)
    role=models.CharField(max_length=50,null=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    objects=CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name_plural="Users"