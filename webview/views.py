import yfinance as yf
import pandas as pd
import requests
import base64
import json
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Max
from api.models import *
from datetime import datetime, timedelta, date
from api.views.trade_analysis import *
from api.views.stock_views import *
from django.conf import settings
from django.db.models import Count
import random


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
        isFundaUpdate = diff_days < 7
    
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
        'isStrongUpdate':bool(isStrongUpdate),
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

def stockScanner(request):
    return render(request, "stock/stock_scanner.html")
def scannerAPI(request):
    filter_type = request.GET.get("filter")

    if filter_type == "penny":
        response = GetPenny(request)
    elif filter_type == "swing":
        response = swingAnalysis(request)
    elif filter_type == "long":
        response = getLong(request)
    elif filter_type == "52low":
        response = get52Low(request)
    elif filter_type == "khigh":
        response = get52High(request)
    else:
        response = None

    if response:
        encoded = response.data.get('data')
        decoded = baseDecode(encoded)
        items = decoded.get('items', [])
    else:
        items = []

    return render(request, "stock/scanner.html", {'items': items})




def baseDecode(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_str = decoded_bytes.decode("utf-8")
    return json.loads(decoded_str)


def analysisWithAi(request, stockName):
    aiResult = groq_analysis(stockName)
    context = {
        "aiResult":aiResult
    }
    return render(request, 'stock/stockDetails.html', context)

def groq_analysis(stock):
    # stock ="Adani green energy"
    stock = StockNames.objects.filter(id=stock).first()
    prompt = f"""
            You are an expert stock market analyst specializing in Indian equities.

            Analyze the stock **{stock.stockName} of stock Code {stock.stockCode} - ** and provide the following in clear headings:

            1. Future Outlook (Short-term 1–4 weeks)
            - Expected trend
            - Momentum and technical indicators
            - Any breakout or breakdown levels

            2. Swing Trading Suitability
            - Is this stock suitable for swing trading now? (Yes/No)
            - Entry range, targets, stop-loss
            - RSI, volume, trend strength, volatility view

            3. Long-Term Investment Suitability
            - What is the long-term future of this company (1–5 years)?
            - Revenue growth, debt levels, expansion plans
            - Pros & cons
            - Long-term price potential (just estimation)

            4. Sector Analysis
            - Is the sector strong or weak?
            - Future demand trends
            - Government or market support

            5. Risk Analysis
            - Key business, financial, and technical risks
            - Whether the current price is risky or safe

            6. Final Verdict
            - What is better: Swing trading or Long-term holding?
            - Who should buy?
            - Who should avoid?

            Be accurate, concise, and avoid generic disclaimers.
            """
    groq_api_key = settings.GROQ_API_KEY
    groq_api_url = settings.GROQ_API_URL
    url = groq_api_url
    headers = {"Authorization": f"Bearer {groq_api_key}"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, json=data, headers=headers)

    # Try parsing JSON
    try:
        response_json = r.json()
    except Exception:
        return JsonResponse({"error": "Invalid JSON from Groq"}, status=500)

    # Check for error from Groq API
    if "error" in response_json:
        return JsonResponse({"error": response_json["error"]}, status=500)

    # Validate response structure
    if "choices" not in response_json or not response_json["choices"]:
        return JsonResponse({"error": "Groq returned no choices"}, status=500)

    result = response_json["choices"][0]["message"]["content"]
    return result


def fetch_multibaggers_view(request):
    booming_stocks = BoomingStock.objects.all().order_by('-growth_factor')
    return render(request, "stock/multibagger.html", {"stocks": booming_stocks})

def fetch_multibaggers(request):
    # You can pass tickers from DB instead of static list
    all_codes = list(StockNames.objects.values_list('yCode', flat=True))
    # tickers = random.sample(all_codes, 10)
    tickers = all_codes
    results = get_recent_boomers(tickers, years=2, min_growth=3, min_target_price=10)
    for stock in results:
        BoomingStock.objects.update_or_create(
            ticker=stock['ticker'],
            defaults={
                'recent_min': stock['recent_min'],
                'min_date': stock['min_date'],
                'current_price': stock['recent_max'],
                'current_date': stock['current_date'],
                'growth_factor': stock['growth_factor']
            }
        )
    return Response({'message': 'Data Fetched Successfully.'}, status=status.HTTP_200_OK)

def get_recent_boomers(tickers, years=1, min_growth=3, min_target_price=10):
    """
    Find stocks that grew rapidly in the last `years` years.
    """
    results = []

    # Calculate start date
    start_date = datetime.now() - timedelta(days=365*years)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date)['Close']

            if hist.empty:
                continue

            recent_min = hist.min()
            recent_max = hist[-1]  # current/latest price
            growth_factor = recent_max / recent_min

            if growth_factor >= min_growth and recent_max >= min_target_price:
                results.append({
                    "ticker": ticker,
                    "recent_min": round(recent_min, 2),
                    "recent_max": round(recent_max, 2),
                    "growth_factor": round(growth_factor, 2),
                    "min_date": hist.idxmin().date(),
                    "current_date": hist.index[-1].date()
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    # Sort by growth factor descending
    results.sort(key=lambda x: x["growth_factor"], reverse=True)
    return results

