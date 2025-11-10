from django.db import models
from django.conf import settings
from budgetManager.models import *
from api.models import *


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
    isProcessed=models.BooleanField(blank=True, null=True, default=False)

    def __int__(self):
        return id

class stockDetails(models.Model):
    finYear=models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name="stkYr")
    month=models.ForeignKey(Months, null=True, blank=True, on_delete=models.CASCADE, related_name="stkMnth")
    stock = models.ForeignKey(StockNames, on_delete=models.CASCADE, null=True, db_column = 'stock', related_name='stkName')
    purchasedOn=models.DateField(null=True, blank=True)
    sellOn=models.DateField(null=True, blank=True)
    purchasedAmnt=models.IntegerField(blank=True, null=True)
    purchasedQty=models.PositiveIntegerField(blank=True, null=True)
    sellAmnt=models.IntegerField(blank=True, null=True)
    sellQty=models.PositiveIntegerField(blank=True, null=True)
    buyBrock=models.IntegerField(blank=True, null=True)
    sellBrock=models.IntegerField(blank=True, null=True)
    totalTax=models.IntegerField(blank=True, null=True)
    totalPurchasedAmnt=models.IntegerField(blank=True, null=True)
    totalSellAmnt=models.IntegerField(blank=True, null=True)
    profit=models.IntegerField(blank=True, null=True)
    refNo=models.PositiveIntegerField(blank=True, null=True)
    transType=models.CharField(max_length=25, null=True, blank=True)

    def __int__(self):
        return id


