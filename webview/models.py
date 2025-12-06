from django.db import models
from django.conf import settings
# Create your models here.
class BoomingStock(models.Model):
    ticker = models.CharField(max_length=50, unique=True)
    recent_min = models.FloatField()
    min_date = models.DateField()
    current_price = models.FloatField()
    current_date = models.DateField()
    growth_factor = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticker} ({self.growth_factor}x)"