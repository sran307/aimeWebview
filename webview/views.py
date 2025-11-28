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
    isSlugEmpty = StockNames.objects.filter(stockSlug__isnull=True).exists()

    max_date = StockNames.objects.aggregate(max_date=Max('strongUpdatedOn'))['max_date']
    if max_date is None:
        isStrongUpdate = False   # No data available
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isStrongUpdate = diff_days < 30
    context = {
        'isHolidayLessThan':isHoliday,
        'isStockNotUsed':isStockNotUsed,
        'isSlugEmpty':isSlugEmpty,
        'isStrongUpdate':isStrongUpdate
    }
    return render(request, 'stock/index.html', context)

