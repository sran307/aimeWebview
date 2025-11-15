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
                    perc=((weekChange/number)+(monthChange/number))
                )
                print('updated')
        except TrendySector.DoesNotExist:
            TrendySector.objects.create(
                sector=sectorData[0]['sector'],
                no=1,
                week=ratio['weekChange'],
                month=ratio['monthChange'],
                perc=((ratio['weekChange']+ratio['monthChange']))
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

@api_view(['POST'])
def swingAnalysis(request):
    
    max_date = SwingStocks.objects.aggregate(Max('date'))['date__max']
    stocks = SwingStocks.objects.filter(date=max_date).values()
    for stock in stocks:
        rank = 1
        comments = StockCommentary.objects.filter(stock=stock['stock_id']).values()
        for comment in comments:
            if comment['mood']=='Positive':
                rank = rank+10
            elif comment['mood'] =='Negative':
                rank=rank-10
            else:
                rank=rank+0
        SwingStocks.objects.filter(stock=stock['stock_id']).update(
            com_rank=rank
        )
        
        ratios = StockRatios.objects.filter(stock=stock['stock_id']).values()
        for ratio in ratios:
            if ratio['divYield']:
                ratio_rank = 1+ratio['divYield']
                rank=rank*ratio_rank
                SwingStocks.objects.filter(stock=stock['stock_id']).update(
                    div_rank=ratio['divYield']
                )
            else:
                SwingStocks.objects.filter(stock=stock['stock_id']).update(
                    div_rank=0
                )
        
        max_date_for_stock = StockHoldings.objects.filter(stock=stock['stock_id']).aggregate(Max('date'))['date__max']
        holdings = StockHoldings.objects.filter(date=max_date_for_stock, stock=stock['stock_id']).values()
        for holding in holdings:
            holding_rank = holding['uPlPctT']+holding['mfPctT']+holding['isPctT']+holding['fiPctT']
            rank=rank+holding_rank
            SwingStocks.objects.filter(stock=stock['stock_id']).update(
                    hol_rank=holding_rank
                )
        
        forecasts = StockForecast.objects.filter(stock=stock['stock_id']).values()
        for forecast in forecasts:
            forecastRank=forecast['buy']-forecast['sell']
            rank = rank+(forecastRank)
            SwingStocks.objects.filter(stock=stock['stock_id']).update(
                    fore_rank=forecastRank
                )
        
        Stock_Ratios = StockLeverageRatios.objects.filter(stock=stock['stock_id']).values()
        for Stock_Ratio in Stock_Ratios:
            rank = rank/Stock_Ratio['debtEq']

        SwingStocks.objects.filter(stock=stock['stock_id']).update(
                    tot_rank=rank
                )

    stockData=[]
    swing_stocks = SwingStocks.objects.filter(date=max_date).order_by('-tot_rank').values()
    for swing_stock in swing_stocks:
        stock_instance = StockNames.objects.filter(id=swing_stock['stock_id']).values()
        for stock in stock_instance:
            try:
                TrendySector.objects.get(sector=stock['sector'])
                totalRank = SwingStocks.objects.filter(stock=stock['id']).values('tot_rank')

                SwingStocks.objects.filter(stock=stock['id']).update(
                    tot_rank=totalRank[0]['tot_rank']+50,
                    is_sector=True
                )
            except TrendySector.DoesNotExist:
                print('no action')

    swing_stocks = SwingStocks.objects.filter(date=max_date, is_sector=True).order_by('-tot_rank').values()
    for swing_stock in swing_stocks:
        stock_instance = StockNames.objects.filter(id=swing_stock['stock_id']).values()
        for stock in stock_instance:
            stock_data = {
                'id': stock['id'],
                'stockName': stock['stockCode']+':'+stock['stockName'],
                'rank': round(swing_stock['tot_rank'], 2)
            }
        stockData.append(stock_data)

    data = {
        'items':stockData
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)


@api_view(['POST'])
def getLong(request):
    dataExist = LongStocks.objects.exists()
    if dataExist:
        tableName = 'long_stocks'
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE {};".format(tableName))
    url = 'https://www.tickertape.in/screener/equity/prebuilt/SCR0026?ref=eq_screener_homepage'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        
        if script_tag:
            json_content = json.loads(script_tag.string)
            # Write the JSON content to a file
            with open('next_data.json', 'w', encoding='utf-8') as file:
                json.dump(json_content, file, ensure_ascii=False, indent=4)
                
            results=json_content.get('props', {}).get('initialReduxState', {}).get('screenerSessionData', {}).get('screenedResults', {})
            for result in results:
                code = result.get('stock', {}).get('info', {}).get('ticker', {})
                ratios= result.get('stock', {}).get('advancedRatios', {})

                LongStocks.objects.create(
                    stock=StockNames.objects.get(stockCode=code), 
                    five_yr_avg_rtn_inst= ratios.get('5Yaroi', {}),
                    five_yr_hist_rvnu_grth= ratios.get('5YrevChg', {}),
                    one_yr_hist_rvnu_grth= ratios.get('rvng', {}),
                    debt_eqty= ratios.get('dbtEqt', {}),
                    roce= ratios.get('roce', {}),
                    item='gems'
                )
                print('inserted')
    except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        
    url = 'https://www.tickertape.in/screener/equity/prebuilt/SCR0005'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        
        if script_tag:
            json_content = json.loads(script_tag.string)
            # Write the JSON content to a file
            with open('next_data.json', 'w', encoding='utf-8') as file:
                json.dump(json_content, file, ensure_ascii=False, indent=4)
                
            results=json_content.get('props', {}).get('initialReduxState', {}).get('screenerSessionData', {}).get('screenedResults', {})
            for result in results:
                code = result.get('stock', {}).get('info', {}).get('ticker', {})
                ratios= result.get('stock', {}).get('advancedRatios', {})

                LongStocks.objects.create(
                    stock=StockNames.objects.get(stockCode=code), 
                    five_yr_roe= ratios.get('5Yroe'),
                    five_yr_hist_rvnu_grth= ratios.get('5YrevChg'),
                    pe= ratios.get('apef'),
                    away_from= ratios.get('52wld'),
                    item='52low'
                )
                print('inserted')
    except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        
    stockData=[]

    long_stocks = LongStocks.objects.all().values()
    for long_stock in long_stocks:
        stock_instance = StockNames.objects.filter(id=long_stock['stock_id']).values()
        max_date = TradeData.objects.filter(stock=long_stock['stock_id']).aggregate(Max('date'))['date__max']
        for stock in stock_instance:
            amount = TradeData.objects.filter(stock=long_stock['stock_id'], date=max_date).values('close').first()
            if amount:
                close_value = round(amount['close'], 2)
            else:
                close_value = 0
            stock_data = {
                'id': stock['id'],
                'stockName': stock['stockCode']+':'+stock['stockName'],
                'amount': close_value,
            }
        stockData.append(stock_data)

    data = {
        'items':stockData
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

@api_view(['POST'])
def get52Low(request):
          
    lstocks = StockRatios.objects.filter(w52Low__lt=500).order_by('away52L').values()
    stockData=[]

    for lstock in lstocks:
        stock_instance = StockNames.objects.filter(id=lstock.get('stock_id')).values()
        for stock in stock_instance:
            amount = lstock.get('w52Low')
            if amount:
                close_value = round(amount, 2)
            else:
                close_value = 0
            stock_data = {
                'id': stock['id'],
                'stockName': stock['stockCode']+':'+stock['stockName'],
                'amount': close_value,
            }
        stockData.append(stock_data)

    data = {
        'items':stockData
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)

@api_view(['POST'])
def get52High(request):
    hstocks = StockRatios.objects.filter(w52High__lt=500).order_by('away52H').values()
    stockData=[]

    for hstock in hstocks:
        stock_instance = StockNames.objects.filter(id=hstock.get('stock_id')).values()
        for stock in stock_instance:
            amount = hstock.get('w52High')
            if amount:
                close_value = round(amount, 2)
            else:
                close_value = 0
            stock_data = {
                'id': stock['id'],
                'stockName': stock['stockCode']+':'+stock['stockName'],
                'amount': close_value,
            }
        stockData.append(stock_data)

    data = {
        'items':stockData
    }
    encodedData = baseEncode(data)
    return Response({'data': encodedData}, status=200)