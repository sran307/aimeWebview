from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from ..models import StockNames, TradeData, Holidays, SwingData, StockCodes, StockRatios, StockHoldings, StockForecast, StockCommentary,SwingStocks,TrendySector,StockLeverageRatios,StockProfitRatios,LongStocks
from django.db.models import Max
from django.db.models import Q
from django.db import connection
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
from rest_framework import generics, status
from encoder import hashUsername, hashPassword, baseEncode
from datetime import datetime, timedelta, date
from api.services.swing_scoring import compute_ranks_for_date
from django.db import transaction

from django.db.models import Subquery, OuterRef

@api_view(['POST'])
def getTrendySector(request):
    # stocks = StockNames.objects.filter(Q(isActive=True) | Q(isFno=True)).values()
    # for stock in stocks:
    #     id = stock['id']
    dataExist = TrendySector.objects.exists()
    if dataExist:
        tableName = 'trendy_sector'
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {};".format(tableName))
    ratios = StockRatios.objects.filter(Q(weekChange__gt=10) | Q(monthChange__gt=20)).values()
    for ratio in ratios:
        stock=ratio['stock_id']
        sectorData = StockNames.objects.filter(id=stock).values('sector')
        try:
            TrendySector.objects.get(sector=sectorData[0]['sector'])
            trendys = TrendySector.objects.filter(sector=sectorData[0]['sector']).values()
            for trendy in trendys:
                number=trendy['no']+1
                weekChange=trendy['week']+ratio['weekChange']
                monthChange=trendy['month']+ratio['monthChange']
                TrendySector.objects.filter(sector=sectorData[0]['sector']).update(
                    no=number,
                    week=weekChange,
                    month=monthChange,
                    perc=((weekChange/number)+(monthChange/number)),
                    updatedOn = date.today()
                )
                print('updated')
        except TrendySector.DoesNotExist:
            TrendySector.objects.create(
                sector=sectorData[0]['sector'],
                no=1,
                week=ratio['weekChange'],
                month=ratio['monthChange'],
                perc=((ratio['weekChange']+ratio['monthChange'])),
                updatedOn = date.today()
            )
            print('data inserted')

    TrendySector.objects.filter(week__lt=10).delete()
    sectors=TrendySector.objects.filter(week__gt=10).order_by('-week').values()
    sector=[{'sector':str(sector['sector'])}for sector in sectors]
    data = {
        'items':sector
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

@api_view(['POST', 'GET'])
def swingAnalysis(request):
    updated = compute_ranks_for_date()
    max_date = SwingStocks.objects.aggregate(max_date=Max('date'))['max_date']
    if not max_date:
        return Response({'items': []})

    q = SwingStocks.objects.filter(date=max_date, is_sector=True).order_by('-tot_rank').select_related('stock')[:50]

    items = []
    for ss in q:
        stock = ss.stock
        items.append({
            'id': stock.id if stock else None,
            'stockName': f"{stock.stockCode}:{stock.stockName}" if stock else None,
            'rank': round(ss.tot_rank, 2),
            'com_rank': ss.com_rank,
            'div_rank': ss.div_rank,
            'hol_rank': ss.hol_rank,
            'fore_rank': ss.fore_rank
        })
    data = {
        'items':items
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

# def swingAnalysis(request):
    
#     max_date = SwingStocks.objects.aggregate(Max('date'))['date__max']
#     stocks = SwingStocks.objects.filter(date=max_date).values()
#     for stock in stocks:
#         rank = 1
#         comments = StockCommentary.objects.filter(stock=stock['stock_id']).values()
#         for comment in comments:
#             if comment['mood']=='Positive':
#                 rank = rank+10
#             elif comment['mood'] =='Negative':
#                 rank=rank-10
#             else:
#                 rank=rank+0
#         SwingStocks.objects.filter(stock=stock['stock_id']).update(
#             com_rank=rank
#         )
        
#         ratios = StockRatios.objects.filter(stock=stock['stock_id']).values()
#         for ratio in ratios:
#             if ratio['divYield']:
#                 ratio_rank = 1+ratio['divYield']
#                 rank=rank*ratio_rank
#                 SwingStocks.objects.filter(stock=stock['stock_id']).update(
#                     div_rank=ratio['divYield']
#                 )
#             else:
#                 SwingStocks.objects.filter(stock=stock['stock_id']).update(
#                     div_rank=0
#                 )
        
#         max_date_for_stock = StockHoldings.objects.filter(stock=stock['stock_id']).aggregate(Max('date'))['date__max']
#         holdings = StockHoldings.objects.filter(date=max_date_for_stock, stock=stock['stock_id']).values()
#         for holding in holdings:
#             holding_rank = holding['uPlPctT']+holding['mfPctT']+holding['isPctT']+holding['fiPctT']
#             rank=rank+holding_rank
#             SwingStocks.objects.filter(stock=stock['stock_id']).update(
#                     hol_rank=holding_rank
#                 )
        
#         forecasts = StockForecast.objects.filter(stock=stock['stock_id']).values()
#         for forecast in forecasts:
#             forecastRank=forecast['buy']-forecast['sell']
#             rank = rank+(forecastRank)
#             SwingStocks.objects.filter(stock=stock['stock_id']).update(
#                     fore_rank=forecastRank
#                 )
        
#         Stock_Ratios = StockLeverageRatios.objects.filter(stock=stock['stock_id']).values()
#         for Stock_Ratio in Stock_Ratios:
#             rank = rank/Stock_Ratio['debtEq']

#         SwingStocks.objects.filter(stock=stock['stock_id']).update(
#                     tot_rank=rank
#                 )

#     stockData=[]
#     swing_stocks = SwingStocks.objects.filter(date=max_date).order_by('-tot_rank').values()
#     for swing_stock in swing_stocks:
#         stock_instance = StockNames.objects.filter(id=swing_stock['stock_id']).values()
#         for stock in stock_instance:
#             try:
#                 TrendySector.objects.get(sector=stock['sector'])
#                 totalRank = SwingStocks.objects.filter(stock=stock['id']).values('tot_rank')

#                 SwingStocks.objects.filter(stock=stock['id']).update(
#                     tot_rank=totalRank[0]['tot_rank']+50,
#                     is_sector=True
#                 )
#             except TrendySector.DoesNotExist:
#                 print('no action')

#     swing_stocks = SwingStocks.objects.filter(date=max_date, is_sector=True).order_by('-tot_rank').values()
#     for swing_stock in swing_stocks:
#         stock_instance = StockNames.objects.filter(id=swing_stock['stock_id']).values()
#         for stock in stock_instance:
#             stock_data = {
#                 'id': stock['id'],
#                 'stockName': stock['stockCode']+':'+stock['stockName'],
#                 'rank': round(swing_stock['tot_rank'], 2)
#             }
#         stockData.append(stock_data)

#     data = {
#         'items':stockData
#     }
#     encodedData = baseEncode(data)
#     return Response({'data': encodedData}, status=200)


def fetch_results(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

    if not script_tag:
        return []

    json_content = json.loads(script_tag.string)
    return json_content.get('props', {}).get('initialReduxState', {}).get('screenerSessionData', {}).get('screenedResults', {})

@api_view(['GET'])
@transaction.atomic
def getLong(request):

    # Clear old records
    LongStocks.objects.all().delete()
    all_new_entries = []

    # -------------------------------
    # SCR0026 — "Gems"
    # -------------------------------
    results_1 = fetch_results(
        'https://www.tickertape.in/screener/equity/prebuilt/SCR0026'
    )

    for r in results_1:
        code = r.get('stock', {}).get('info', {}).get('ticker')
        ratios = r.get('stock', {}).get('advancedRatios', {})

        try:
            stock = StockNames.objects.get(stockCode=code)
        except StockNames.DoesNotExist:
            continue

        score = calculate_long_score(ratios)
        recommendation = get_recommendation(score)

        all_new_entries.append(LongStocks(
            stock=stock,
            score=score,
            recommendation=recommendation,
            five_yr_avg_rtn_inst=ratios.get('5Yaroi'),
            five_yr_hist_rvnu_grth=ratios.get('5YrevChg'),
            one_yr_hist_rvnu_grth=ratios.get('rvng'),
            debt_eqty=ratios.get('dbtEqt'),
            roce=ratios.get('roce'),
            item='gems'
        ))

    # -------------------------------
    # SCR0005 — 52 Week Low
    # -------------------------------
    results_2 = fetch_results(
        'https://www.tickertape.in/screener/equity/prebuilt/SCR0005'
    )

    for r in results_2:
        code = r.get('stock', {}).get('info', {}).get('ticker')
        ratios = r.get('stock', {}).get('advancedRatios', {})

        try:
            stock = StockNames.objects.get(stockCode=code)
        except StockNames.DoesNotExist:
            continue

        all_new_entries.append(LongStocks(
            stock=stock,
            five_yr_roe=ratios.get('5Yroe'),
            five_yr_hist_rvnu_grth=ratios.get('5YrevChg'),
            pe=ratios.get('apef'),
            away_from=ratios.get('52wld'),
            item='52low'
        ))

    # -------------------------------
    # Bulk insert
    # -------------------------------
    LongStocks.objects.bulk_create(all_new_entries)

    # -------------------------------
    # Fetch LongStocks with prices
    # -------------------------------
    long_stocks = list(
        LongStocks.objects.select_related('stock').values(
            'id',
            'stock_id',
            'score',
            'recommendation'
        )
    )

    stock_ids = [ls['stock_id'] for ls in long_stocks]

    # -------------------------------
    # Latest close price using Subquery
    # -------------------------------
    latest_close_subquery = (
        TradeData.objects
        .filter(stock_id=OuterRef('pk'))
        .order_by('-date')
        .values('close')[:1]
    )

    price_lookup = {
        s['id']: s['close']
        for s in StockNames.objects.filter(id__in=stock_ids)
        .annotate(close=Subquery(latest_close_subquery))
        .values('id', 'close')
    }

    # -------------------------------
    # Build final response
    # -------------------------------
    stockData = []

    for ls in long_stocks:
        sid = ls['stock_id']
        stock = StockNames.objects.get(id=sid)

        stockData.append({
            "id": sid,
            "stockName": f"{stock.stockCode}:{stock.stockName}",
            "amount": round(price_lookup.get(sid, 0) or 0, 2),
            "score": ls['score'],
            "recommendation": ls['recommendation'],
        })

    encodedData = baseEncode({"items": stockData})

    return Response({'data': encodedData}, status=200)

# def getLong(request):
#     dataExist = LongStocks.objects.exists()
#     if dataExist:
#         tableName = 'long_stocks'
#         with connection.cursor() as cursor:
#             cursor.execute("TRUNCATE TABLE {};".format(tableName))
#     url = 'https://www.tickertape.in/screener/equity/prebuilt/SCR0026?ref=eq_screener_homepage'

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Check if the request was successful

#         soup = BeautifulSoup(response.content, 'html.parser')

#         script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        
#         if script_tag:
#             json_content = json.loads(script_tag.string)
#             # Write the JSON content to a file
#             with open('next_data.json', 'w', encoding='utf-8') as file:
#                 json.dump(json_content, file, ensure_ascii=False, indent=4)
                
#             results=json_content.get('props', {}).get('initialReduxState', {}).get('screenerSessionData', {}).get('screenedResults', {})
#             for result in results:
#                 code = result.get('stock', {}).get('info', {}).get('ticker', {})
#                 ratios= result.get('stock', {}).get('advancedRatios', {})

#                 LongStocks.objects.create(
#                     stock=StockNames.objects.get(stockCode=code), 
#                     five_yr_avg_rtn_inst= ratios.get('5Yaroi', {}),
#                     five_yr_hist_rvnu_grth= ratios.get('5YrevChg', {}),
#                     one_yr_hist_rvnu_grth= ratios.get('rvng', {}),
#                     debt_eqty= ratios.get('dbtEqt', {}),
#                     roce= ratios.get('roce', {}),
#                     item='gems'
#                 )
#                 print('inserted')
#     except requests.exceptions.RequestException as e:
#             print(f"An error occurred: {e}")
        
#     url = 'https://www.tickertape.in/screener/equity/prebuilt/SCR0005'

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Check if the request was successful

#         soup = BeautifulSoup(response.content, 'html.parser')

#         script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        
#         if script_tag:
#             json_content = json.loads(script_tag.string)
#             # Write the JSON content to a file
#             with open('next_data.json', 'w', encoding='utf-8') as file:
#                 json.dump(json_content, file, ensure_ascii=False, indent=4)
                
#             results=json_content.get('props', {}).get('initialReduxState', {}).get('screenerSessionData', {}).get('screenedResults', {})
#             for result in results:
#                 code = result.get('stock', {}).get('info', {}).get('ticker', {})
#                 ratios= result.get('stock', {}).get('advancedRatios', {})

#                 LongStocks.objects.create(
#                     stock=StockNames.objects.get(stockCode=code), 
#                     five_yr_roe= ratios.get('5Yroe'),
#                     five_yr_hist_rvnu_grth= ratios.get('5YrevChg'),
#                     pe= ratios.get('apef'),
#                     away_from= ratios.get('52wld'),
#                     item='52low'
#                 )
#                 print('inserted')
#     except requests.exceptions.RequestException as e:
#             print(f"An error occurred: {e}")
        
#     stockData=[]

#     long_stocks = LongStocks.objects.all().values()
#     for long_stock in long_stocks:
#         stock_instance = StockNames.objects.filter(id=long_stock['stock_id']).values()
#         max_date = TradeData.objects.filter(stock=long_stock['stock_id']).aggregate(Max('date'))['date__max']
#         for stock in stock_instance:
#             amount = TradeData.objects.filter(stock=long_stock['stock_id'], date=max_date).values('close').first()
#             if amount:
#                 close_value = round(amount['close'], 2)
#             else:
#                 close_value = 0
#             stock_data = {
#                 'id': stock['id'],
#                 'stockName': stock['stockCode']+':'+stock['stockName'],
#                 'amount': close_value,
#             }
#         stockData.append(stock_data)

#     data = {
#         'items':stockData
#     }
#     encodedData = baseEncode(data)
#     return Response({'data': encodedData}, status=200)
def calculate_long_score(r):
    """
    r = ratios dict from tickertape
    returns score 0 - 100
    """

    score = 0

    # 1️⃣ ROE (Max 15 points)
    roe = r.get('5Yroe') or 0
    if roe > 25:
        score += 15
    elif roe > 15:
        score += 10
    elif roe > 10:
        score += 5

    # 2️⃣ ROCE (Max 15 points)
    roce = r.get('roce') or 0
    if roce > 25:
        score += 15
    elif roce > 15:
        score += 10
    elif roce > 10:
        score += 5

    # 3️⃣ Debt/Equity (Max 10 points)
    de = r.get('dbtEqt') or 0
    if de < 0.2:
        score += 10
    elif de < 0.5:
        score += 7
    elif de < 1:
        score += 5

    # 4️⃣ 5 Year Revenue Growth (Max 10)
    rev5 = r.get('5YrevChg') or 0
    if rev5 > 20:
        score += 10
    elif rev5 > 10:
        score += 7
    elif rev5 > 5:
        score += 5

    # 5️⃣ 1Y Revenue Growth (Max 5)
    rev1 = r.get('rvng') or 0
    if rev1 > 20:
        score += 5
    elif rev1 > 10:
        score += 3
    elif rev1 > 5:
        score += 2

    # 6️⃣ Valuation: PE Ratio (Max 10)
    pe = r.get('apef') or 0
    if 10 < pe < 20:
        score += 10
    elif 20 < pe < 30:
        score += 7
    elif pe < 10:
        score += 5

    # 7️⃣ Distance from 52W Low (Max 10)
    dist_52_low = r.get('52wld') or 0  # % away from low
    if dist_52_low < 10:
        score += 10
    elif dist_52_low < 20:
        score += 7

    # 8️⃣ 5-Year Annual Returns (Max 10)
    r5 = r.get('5Yaroi') or 0
    if r5 > 20:
        score += 10
    elif r5 > 12:
        score += 7
    elif r5 > 5:
        score += 5

    return min(score, 100)

def get_recommendation(score):
    if score >= 80:
        return "Strong Buy"
    elif score >= 65:
        return "Buy"
    elif score >= 50:
        return "Hold"
    elif score >= 35:
        return "Avoid"
    else:
        return "Sell"


@api_view(['POST', 'GET'])
def get52Low(request):
          
#     lstocks = StockRatios.objects.filter(w52Low__lt=500).order_by('away52L').values()
#     stockData=[]

#     for lstock in lstocks:
#         stock_instance = StockNames.objects.filter(id=lstock.get('stock_id')).values()
#         for stock in stock_instance:
#             amount = lstock.get('w52Low')
#             if amount:
#                 close_value = round(amount, 2)
#             else:
#                 close_value = 0
#             stock_data = {
#                 'id': stock['id'],
#                 'stockName': stock['stockCode']+':'+stock['stockName'],
#                 'amount': close_value,
#             }
#         stockData.append(stock_data)

#     data = {
#         'items':stockData
#     }
#     encodedData = baseEncode(data)
#     return Response({'data': encodedData}, status=200)

    stocks = StockRatios.objects.filter(
        away52L__gt=0,
        away52L__lt=7,
        w52Low__lt=1000
    ).select_related('stock')

    results = []

    for r in stocks:
        s = r.stock
        
        # Profit ratios
        pr = getattr(s, 'profit_stock_name', None)
        if not pr: 
            continue

        # Leverage
        lr = getattr(s, 'leverage_stock_name', None)
        if not lr: 
            continue

        # Forecast
        fr = getattr(s, 'forecast_stock_name', None)

        # --- Rule 1: Fundamentals ---
        if pr.eps <= 0 or pr.roe < 12 or lr.debtEq > 1:
            continue

        # --- Rule 2: Trend ---
        if r.dayChange < 1:                  # buyers not entered yet
            continue
        if r.weekChange < -2:
            continue
        if r.monthChange < -10 or r.monthChange > -2:
            continue

        # --- Rule 3: Beta ---
        if r.beta < 0.8 or r.beta > 1.5:
            continue

        # --- Rule 4: Forecast ---
        if fr and fr.buy < 55:
            continue

        # --- SCORE SYSTEM ---
        score = 0

        trendScore = (r.dayChange * 2) + r.weekChange + abs(r.monthChange)
        fundaScore = min(pr.roe, 20)
        forecastScore = fr.buy if fr else 0
        bottomScore = max(7 - r.away52L, 0) * 4

        finalScore = trendScore + fundaScore + forecastScore + bottomScore

        results.append({
            'id': s.id,
            'stock': f"{s.stockCode}: {s.stockName}",
            'lastPrice': r.lastPrice,
            '52low': r.w52Low,
            'away52L': r.away52L,
            'dayChange': r.dayChange,
            'weekChange': r.weekChange,
            'monthChange': r.monthChange,
            'score': round(finalScore, 2)
        })

    results = sorted(results, key=lambda x: x['score'], reverse=True)

    data = {
        'items':results
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

@api_view(['POST', 'GET'])
def get52High(request):
    # hstocks = StockRatios.objects.filter(w52High__lt=500).order_by('away52H').values()
    stockData=[]

    # for hstock in hstocks:
    #     stock_instance = StockNames.objects.filter(id=hstock.get('stock_id')).values()
    #     for stock in stock_instance:
    #         amount = hstock.get('w52High')
    #         if amount:
    #             close_value = round(amount, 2)
    #         else:
    #             close_value = 0
    #         stock_data = {
    #             'id': stock['id'],
    #             'stockName': stock['stockCode']+':'+stock['stockName'],
    #             'amount': close_value,
    #         }
    #     stockData.append(stock_data)
    stocks = StockNames.objects.all()
    for stock in stocks:
        ratios = StockRatios.objects.filter(stock=stock).first()
        if not ratios:
            continue 

        decision = isTradeable52High(stock, ratios)

        stockData.append({
            "id": stock.id,
            "stockName": stock.stockName,
            "close": ratios.lastPrice,
            "decision": decision,
        })

    data = {
        'items':stockData
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

def isTradeable52High(stock, ratios):
    """
    stock = StockNames object
    ratios = StockRatios object
    """

    try:
        close = ratios.close
        high = ratios.high
        low = ratios.low
        prev_high = ratios.w52High
        volume = ratios.volume
        avg_vol = ratios.avg20Vol

        # ---- 1. Price breakout ----
        price_breakout = close > prev_high

        # ---- 2. Volume breakout ----
        vol_breakout = volume >= (avg_vol * 1.5 if avg_vol else 0)

        # ---- 3. Wick strength (buyers support) ----
        buyers_wick = close > (low + (high - low) * 0.40)

        # ---- 4. Fundamentals ----
        fundamentals = (
            (ratios.eps > 0) +
            (ratios.roe >= 12) +
            (ratios.debtEq <= 1)
        )
        fundamentals_ok = fundamentals >= 2   # at least 2 conditions true

        # ---- Decision ----
        if price_breakout and vol_breakout and buyers_wick and fundamentals_ok:
            return "ENTRY"

        if price_breakout and buyers_wick:
            return "WAIT"     # breakout but no volume

        return "AVOID"

    except Exception as e:
        return f"ERROR: {str(e)}"
