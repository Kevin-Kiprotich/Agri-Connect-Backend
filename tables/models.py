from django.db import models

# Create your models here.
class SUMS(models.Model):
    grantee=models.CharField(max_length=255, null=False)
    year=models.IntegerField(null=False)
    quota=models.CharField(null=False,max_length=10)
    file=models.FileField(upload_to='files',null=False,unique=False)

    class Meta:
        verbose_name_plural='SUMS'

class AnnualTotals(models.Model):
    grantee=models.CharField(max_length=100,null=False)
    year=models.CharField(max_length=25,null=False)
    file=models.FileField(upload_to='annual_totals',null=False)

    class Meta:
        verbose_name_plural='Annual Totals'

class CumulativeTotals(models.Model):
    grantee=models.CharField(max_length=100,null=False)
    file=models.FileField(upload_to='cummulative_totals',null=False)