from django.db import models

# Create your models here.
class SUMS(models.Model):
    grantee=models.CharField(max_length=255, null=False)
    year=models.IntegerField(null=False)
    quota=models.CharField(null=False,max_length=10)
    file=models.FileField(upload_to='files',null=False,unique=False)

    class Meta:
        verbose_name_plural='SUMS'