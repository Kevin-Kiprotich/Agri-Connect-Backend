from django.db import models

# Create your models here.
class SUMS(models.Model):
    grantees=models.CharField(max_length=255, null=False)
    year=models.IntegerField(null=False)
    quota=models.IntegerField(null=False)
    file=models.FileField(upload_to='files',null=False,unique=True)