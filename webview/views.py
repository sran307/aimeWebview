from django.shortcuts import render
from django.utils import timezone
from django.db.models import Max
from api.models import *

def home(request):
    return render(request, 'main/home.html')

def stockAnalyser(request):
    max_holiday = Holidays.objects.aggregate(Max('holiday'))['holiday__max']
    isHoliday = max_holiday and max_holiday > timezone.now().date()

    isStockNotUsed = StockCodes.objects.filter(isUsed=False).exists()
    context = {
        'isHolidayLessThan':isHoliday,
        'isStockNotUsed':isStockNotUsed,
    }
    return render(request, 'stock/index.html', context)

