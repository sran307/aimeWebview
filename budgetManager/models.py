from django.db import models
from django.conf import settings

class FinancialYear(models.Model):
    year = models.TextField(blank=True)
    yearDesc = models.CharField(max_length=25, blank=True)
    startDate = models.DateField(blank=True)
    endDate = models.DateField(blank=True)
    def __str__(self):
        return self.yearDesc

class Months(models.Model):
    monthDesc = models.CharField(max_length=25)
    monthAbbr = models.CharField(max_length=25)

    def __str__(self):
        return self.monthDesc

class Sheet(models.Model):
    finYear=models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name="finIds")
    month=models.ForeignKey(Months, null=True, blank=True, on_delete=models.CASCADE, related_name="months")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cell(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, related_name="cells")
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    value = models.CharField(max_length=100, blank=True)
    formula = models.CharField(max_length=255, blank=True, null=True)
    version = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sheet", "row", "col")
        indexes = [models.Index(fields=["sheet", "row", "col"])]

    def __str__(self):
        return f"Cell {self.row},{self.col} @ {self.sheet_id}"


class CellChange(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name="changes")
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()

    class Meta:
        ordering = ("-changed_at",)

class Items(models.Model):
    desc = models.CharField(max_length=100, null=True)
    isExpensive = models.BooleanField(default=False)
    
    def __int__(self):
        return id

class monthlyData(models.Model):
    VALUE_TYPE_CHOICES = [
        ('ET', 'Expected Total'),
        ('MD', 'Monthly Data'),
        ('NIC', 'NIC'),
        ('PR', 'Prathibha'),
    ]
    finYear=models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name="finyrs")
    month=models.ForeignKey(Months, null=True, blank=True, on_delete=models.CASCADE, related_name="monthids") 
    item=models.ForeignKey(Items, null=True, blank=True, on_delete=models.CASCADE, related_name="items") 
    datedOn=models.DateField(null=True)
    amount = models.PositiveIntegerField()
    valueType = models.CharField(max_length=10, choices=VALUE_TYPE_CHOICES, default='MD', null=True)
    
    def __int__(self):
        return id

