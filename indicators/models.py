from django.db import models

# Create your models here.
class SUMSIndicators(models.Model):
    code=models.CharField(max_length=10,null=False)