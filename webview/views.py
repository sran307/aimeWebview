from django.shortcuts import render
from django.utils import timezone
from django.db.models import Max
from api.models import *
from datetime import datetime, timedelta, date

def home(request):
    return render(request, 'main/home.html')

def stockAnalyser(request):
    max_holiday = Holidays.objects.aggregate(Max('holiday'))['holiday__max']
    isHoliday = max_holiday and max_holiday > timezone.now().date()

    isStockNotUsed = StockCodes.objects.filter(isUsed=False).exists()
    isSlugEmpty = StockNames.objects.filter(stockSlug__isnull=True).exists()

    max_date = StockNames.objects.aggregate(max_date=Max('strongUpdatedOn'))['max_date']
    lastUpdateDate = max_date
    
    if max_date is None:
        isStrongUpdate = False
        lastUpdatedCount1=0
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isStrongUpdate = diff_days < 30
        lastUpdatedCount1 = StockNames.objects.filter(strongUpdatedOn=max_date).count()

    max_date = StockCodes.objects.aggregate(max_date=Max('lastFetchedOn'))['max_date']
    if max_date is None:
        isFetchStockCode = False   # No data available
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isFetchStockCode = diff_days < 30

    max_date = StockNames.objects.aggregate(max_date=Max('sectorUpdatedOn'))['max_date']
    if max_date is None:
        isSectorUpdate = False
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isSectorUpdate = diff_days < 30

    max_date = StockProfitRatios.objects.aggregate(max_date=Max('updatedOn'))['max_date']
    if max_date is None:
        isFundaUpdate = False
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isFundaUpdate = diff_days < 30
    
    max_date = TrendySector.objects.aggregate(max_date=Max('updatedOn'))['max_date']
    if max_date is None:
        isTrendyUpdate = False
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isTrendyUpdate = diff_days < 7

    max_date = TradeData.objects.aggregate(max_date=Max('updatedAt'))['max_date']
    if max_date is None:
        isDailyUpdate = False
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isDailyUpdate = diff_days < 1

    max_date = MultibaggerScore.objects.aggregate(max_date=Max('updatedOn'))['max_date']
    if max_date is None:
        isPennyUpdate = False
    else:
        current_date = date.today()
        diff_days = (current_date - max_date).days
        isPennyUpdate = diff_days < 30

    context = {
        'isHolidayLessThan':isHoliday,
        'isStockNotUsed':isStockNotUsed,
        'isSlugEmpty':isSlugEmpty,
        'isStrongUpdate':isStrongUpdate,
        'isFetchStockCode':isFetchStockCode,
        'isSectorUpdate':isSectorUpdate,
        'isFundaUpdate':isFundaUpdate,
        'isTrendyUpdate':isTrendyUpdate,
        'isDailyUpdate':isDailyUpdate,
        'lastUpdateDate':lastUpdateDate,
        'lastUpdatedCount1':lastUpdatedCount1,
        'isPennyUpdate':isPennyUpdate
    }
    return render(request, 'stock/index.html', context)

