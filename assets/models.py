from django.db import models
from django.conf import settings
from budgetManager.models import *

class stockHeadings(models.Model):
    itemName = models.CharField(max_length=50, null=True)
    
    def __id__(self):
        return id

class stockTransactions(models.Model):
    VALUE_TYPE_CHOICES = [
        ('INTRA', 'Intra day trading'),
        ('MTFT', 'Margin Trading Fund'),
        ('SWING', 'Swing Trading'),
        ('LONG', 'Long Posintion'),
        ('OPTION', 'OPtion trading data'),
        ('MF', 'Mutual Fund')
    ]
    finYear=models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name="transYr")
    month=models.ForeignKey(Months, null=True, blank=True, on_delete=models.CASCADE, related_name="transMnth") 
    heading=models.ForeignKey(stockHeadings, null=True, blank=True, on_delete=models.CASCADE, related_name="transHead")
    transValue=models.TextField(blank=True, null=True)
    transType=models.CharField(max_length=15, choices=VALUE_TYPE_CHOICES, blank=True, null=True)
    refNo = models.PositiveIntegerField(blank=True, null=True)
    slNo = models.PositiveIntegerField(blank=True, null=True)

    def __int__(self):
        return id
