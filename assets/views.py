from nsepython import nse_index, nse_preopen, indiavix, nse_get_index_quote
import yfinance as yf
from django.shortcuts import render
from .models import *
from budgetManager.models import *
from api.models import *
from django.http import HttpResponse
import calendar
from datetime import date, datetime
from collections import defaultdict
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import F
from pprint import pprint
from .forms import *
from django.db.models import Sum
from decimal import Decimal
import requests
from django.conf import settings

def assets(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    finYears = FinancialYear.objects.all()

    divAmount = dividentDetails.objects.filter(finYear=finYear).aggregate(total=Sum('amount'))['total'] or Decimal(0)
    optionProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='OPTION').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    longProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='LONG').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    swingProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='SWING').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    intraProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='INTRA').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    mtfProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='MTF').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    mfProfit = stockDetails.objects.filter(buyFinYear=finYear, transType='MF').aggregate(total=Sum('profit'))['total'] or Decimal(0)
    totalTax = stockDetails.objects.filter(buyFinYear=finYear).aggregate(total=(Sum('buyBrock')+Sum('sellBrock')))['total'] or Decimal(0)

    overallProfit = stockDetails.objects.aggregate(total=Sum('profit'))['total'] or Decimal(0)
    overallTax = stockDetails.objects.aggregate(total=(Sum('buyBrock')+Sum('sellBrock')))['total'] or Decimal(0)

    totalProfit = divAmount+optionProfit+longProfit+swingProfit+intraProfit+mtfProfit+mfProfit
    context={
        'divAmount': divAmount,
        'optionProfit':optionProfit,
        'longProfit':longProfit,
        'swingProfit':swingProfit,
        'intraProfit':intraProfit,
        'mtfProfit':mtfProfit,
        'totalProfit':totalProfit,
        'mfProfit':mfProfit,
        'finYears':finYears,
        'finYear':finYear,
        'overallProfit':overallProfit,
        'overallTax':overallTax,
        'totalTax':totalTax

    }
    return render(request, 'assets/index.html', context)

def indexManager(request, transType):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType=transType)

    context={
        'stockDetails':stockData,
        'transType':transType
    }
    return render(request, 'assets/indexManager.html', context)

def transManager(request, transType):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    current_month = date.today().month
    month = Months.objects.get(id=current_month)

    finYears = FinancialYear.objects.all()

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, transType=transType)
    data_dict = {}
    for d in transactions:
        key = (d.heading.id, d.slNo, d.transType)
        data_dict[key] = d.transValue

        data_dict[('reference', d.slNo, d.transType)] = d.refNo

    context={
        'stockHeadings':headings,
        'month':month,
        'finYear':finYear,
        'finYears':finYears,
        'data_dict':data_dict,
        'numbers': range(1, 101),
        'transType': transType
    }
    return render(request, 'assets/transManager.html', context)

def dividentManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()
    dividends = dividentDetails.objects.filter(finYear=finYear)
    context={
        'finYear':finYear,
        'finYears':finYears,
        'dividends':dividends
    }
    return render(request, 'assets/divManager.html', context)

def addDividend(request):
    if request.method == 'POST':
        form = DividentDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error"})
    else:
        form = DividentDetailsForm()

    return render(request, 'assets/divident_form.html', {'form': form})


def saveTrans(request):
    if request.method == "POST":
        # date_str = request.POST.get("date")
        value = request.POST.get("value")
        item_id = request.POST.get("item")
        month_id = request.POST.get("month")
        year_id = request.POST.get("year")
        valueType = request.POST.get("valueType")
        slNo = request.POST.get("slNo")
        refValue = request.POST.get("refValue")
        obj, created = stockTransactions.objects.update_or_create(
            finYear_id=year_id,
            month_id=month_id,
            heading_id=item_id,
            slNo=slNo,
            defaults={"transValue": value or '', 'refNo':refValue or 0},
            transType=valueType
        )
        return JsonResponse({"status": "ok", "created": created})

def showStocks(request):
    stocks = StockNames.objects.all()
    context={
        'stocks':stocks
    }
    return render(request, 'assets/showStocks.html', context)

def showMfs(request):
    mfs = mfNames.objects.filter(isActive=True)
    context={
        'mfs':mfs
    }
    return render(request, 'assets/showMf.html', context)


def process(request, transType, processType):
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except Exception:
            return None

    if processType == 'N':
        rows = (
            stockTransactions.objects
            .filter(transType=transType, isProcessed=False)
            .select_related('heading')
            .values(
                'refNo',
                'slNo',
                'finYear',
                heading_desc=F('heading__itemName'),
                transValue1=F('transValue')
            )
            .order_by('refNo', 'slNo', 'heading_id')
        )
    elif processType == 'A':
        rows = (
            stockTransactions.objects
            .filter(transType=transType)
            .select_related('heading')
            .values(
                'refNo',
                'slNo',
                'finYear',
                heading_desc=F('heading__itemName'),
                transValue1=F('transValue')
            )
            .order_by('refNo', 'slNo', 'heading_id')
        )
    grouped_data = {}
    for row in rows:
        ref_no = row['refNo']
        sl_no = row['slNo']
        heading = row['heading_desc']
        value = row['transValue1']
        finYear  = row['finYear']

        grouped_data.setdefault(ref_no, {})
        grouped_data[ref_no].setdefault(sl_no, {})
        grouped_data[ref_no][sl_no][heading] = value
        grouped_data[ref_no][sl_no]['finYear'] = finYear

    for ref_no, sl_data in grouped_data.items():
        buy_data = None
        sell_data = None

        for sl_no, data in sl_data.items():
            transaction_type = data.get('transaction', '').lower()
            if transaction_type == 'buy':
                buy_data = data
                if transType == 'OPTION':
                    stock_obj = None
                    mfName = None
                    optionName=buy_data.get('stockName')
                elif transType == 'MF':
                    stock_obj = None
                    optionName = None
                    mfName=mfNames.objects.filter(mfName=buy_data.get('stockName')).first()
                else:
                    stock_name = buy_data.get('stockName')
                    stock_obj = StockNames.objects.filter(stockName=stock_name).first()
                    optionName=None
                    mfName=None

                purchased_qty = float(buy_data.get('quantity') or 0)
                purchased_rate = float(buy_data.get('amntPerStock') or 0)
                purchasedBrkg = float(buy_data.get('brockerage') or 0)
                total_purchased = (purchased_qty * purchased_rate)+purchasedBrkg

                buyReason = buy_data.get('buyReason') or ''
                buyRemarks = buy_data.get('remarks') or ''
                buyYear = buy_data.get('finYear') or ''
                finYear = FinancialYear.objects.filter(id=buyYear).first()

                stockDetails.objects.update_or_create(
                    refNo=ref_no,
                    transType=transType,
                    defaults={
                        'stock': stock_obj,
                        'purchasedOn': parse_date(buy_data.get('transDate')),
                        'purchasedQty': purchased_qty,
                        'purchasedAmnt': purchased_rate,
                        'totalPurchasedAmnt': total_purchased,
                        'buyBrock':purchasedBrkg,
                        'purchasedReason':buyReason,
                        'buyRemarks': buyRemarks,
                        'buyFinYear':finYear,
                        'optionName':optionName,
                        'mfName':mfName
                    }
                )
            if transaction_type == 'sell':
                sell_data = data
                if transType == 'OPTION':
                    stock_obj = None
                    mfName = None
                    optionName=sell_data.get('stockName')
                elif transType == 'MF':
                    stock_obj = None
                    optionName = None
                    mfName=mfNames.objects.filter(mfName=sell_data.get('stockName')).first()
                else:
                    stock_name = sell_data.get('stockName')
                    stock_obj = StockNames.objects.filter(stockName=stock_name).first()
                    optionName=None
                    mfName=None
                sell_qty = float(sell_data.get('quantity') or 0)
                sell_rate = float(sell_data.get('amntPerStock') or 0)
                sellBrkg = float(sell_data.get('brockerage') or 0)

                total_sold = (sell_qty * sell_rate)-sellBrkg
                sellReason = sell_data.get('sellReason') or ''
                sellRemarks = sell_data.get('remarks') or ''
                sellYear = sell_data.get('finYear') or ''
                finYear = FinancialYear.objects.filter(id=sellYear).first()

                stockDetails.objects.update_or_create(
                    refNo=ref_no,
                    transType=transType,
                    defaults={
                        'stock': stock_obj,
                        'sellOn': parse_date(sell_data.get('transDate')),
                        'sellQty': sell_qty,
                        'sellAmnt': sell_rate,
                        'totalSellAmnt': total_sold,
                        'sellBrock':sellBrkg,
                        'sellReason':sellReason,
                        'sellRemarks':sellRemarks,
                        'sellFinYear':finYear,
                        'optionName':optionName,
                        'mfName':mfName
                    }
                )
            
            if buy_data and sell_data:
                profit = total_sold - total_purchased
                stockDetails.objects.update_or_create(
                    refNo=ref_no,
                    transType=transType,
                    defaults={
                        'profit': profit,
                    }
                )
                stockTransactions.objects.filter(
                    refNo=ref_no,
                    transType=transType
                ).update(
                        isProcessed= True
                )
    return JsonResponse({'status': 'success', 'message':'Data Processed Successfully.'})  


def clearData(request):
    """
    Deletes all stockTransactions where transValue is either NULL or empty string.
    Returns the number of deleted rows.
    """
    deleted_count, _ = stockTransactions.objects.filter(
        transValue__isnull=True
    ).delete()

    deleted_empty_count, _ = stockTransactions.objects.filter(
        transValue=''
    ).delete()

    total_deleted = deleted_count + deleted_empty_count
    print(f"{total_deleted} empty transactions deleted.")
    return JsonResponse({'status': 'success', 'message':'cache cleared Successfully.'})

def longAnalysisWithAi(request, stockId, detId):
    aiResult = groq_long_analysis(stockId, detId)
    context = {
        "aiResult":aiResult
    }
    return render(request, 'stock/stockDetails.html', context)

def groq_long_analysis(stock, detId):
    # stock ="Adani green energy"
    stock = StockNames.objects.filter(id=stock).first()
    stockDet = stockDetails.objects.filter(id=detId).first()
    prompt = f"""
        You are an expert stock market analyst specializing in Indian equities.

        I have picked the following stock for long-term investment and now I want to make a wise decision based on the current situation.

        Stock details:
        - Name: {stock.stockName}
        - Code: {stock.stockCode}
        - Purchased on: {stockDet.purchasedOn}
        - Purchased price: ₹{stockDet.purchasedAmnt}
        - Quantity: {stockDet.purchasedQty}
        - Current price: check it  # if available

        Please provide analysis with clear headings:

        1. **Long-Term Hold Assessment**  
        - Is it wise to hold this stock for the long term? Why or why not?

        2. **Current Action Recommendation**  
        - What action should I take now? (Hold, Add More, Partial Exit, Full Exit)  
        - Suggested entry/exit price levels if relevant.

        3. **Future Outlook if Held**  
        - Expected growth or risk if I continue holding.  
        - Potential price range for the next 1–3 years (concise estimation).

        Be **accurate, concise, and actionable**, avoid generic disclaimers or vague statements. Format your response with **headings** for clarity.
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

def optionAnalysisWithAi(request):
    aiResult = groq_option_analysis()
    context = {
        "aiResult":aiResult
    }
    return render(request, 'stock/stockDetails.html', context)

def groq_option_analysis():
    nifty_data = fetch_nifty_data()
    print(nifty_data)

    prompt = f"""
        You are an options analyst specialized in the Indian stock market.  
        Your task is to recommend a safe, long-only NIFTY option trade based on
        pre-market data.  
        Focus on risk-controlled, conservative strategies suitable for beginners.

        Always follow these rules:
        - Only suggest LONG trades (BUY CE or BUY PE). No selling or shorting.
        - Never suggest naked risky trades. Stick to ATM or slightly OTM only.
        - Avoid suggesting weekly expiry trades if volatility is extremely high.
        - Avoid suggesting trades during major events (Budget, RBI policy, Fed decision).
        - Only give a trade when data clearly supports direction; otherwise suggest NO TRADE.
        - Risk per trade must not exceed 1-2% of account.
        - Maintain accuracy, discipline, and safety.

        Input Data Format (User Provides):
            - NIFTY previous close: {nifty_data['previous_close']}
            - SGX/GIFT NIFTY: {nifty_data['sgx_change']}
            - Pre-market change (%): {nifty_data['pre_market_change']}
            - Sector sentiment: Banking: {nifty_data['sector_sentiment']['BANK']}, IT: {nifty_data['sector_sentiment']['IT']}, Auto: {nifty_data['sector_sentiment']['AUTO']}
            - India VIX: {nifty_data['vix']}
            - Major global cues: Positive  # You can hardcode or fetch from an API
            - Support & resistance levels: Support: {nifty_data['support']}, Resistance: {nifty_data['resistance']}

        Your Output Format:
        1. Pre-market bias: Bullish / Bearish / Neutral
        2. Reason for bias (3–5 bullet points)
        3. Suggested trade (LONG ONLY):
        - Buy NIFTY CE or Buy NIFTY PE
        - Strike (ATM or nearest OTM only)
        - Expiry (Weekly or Monthly — choose safer one)
        4. Entry zone (premium range)
        5. Stop-loss (premium based)
        6. Safe target (premium based)
        7. Risk level: Low / Medium / High
        8. When to stay out: Mention if NO TRADE is safer.

        If direction is unclear → Output "NO TRADE — Market not giving a clear bias."
        Never hallucinate data. Only read and interpret the user input.

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

from nsepython import nse_index, nse_preopen, indiavix
import pandas as pd

def fetch_nifty_data():
    import pandas as pd
    from nsepython import nse_index, nse_preopen, indiavix

    data = {}

    # 1️⃣ Fetch full index list (DataFrame)
    df = safe_call(nse_index())  # this is a pandas DataFrame)
    # print(df.head())

    # Find NIFTY 50 row
    nifty_row = df[df["indexName"] == "NIFTY 50"].iloc[0]

    # Helper to convert numeric strings like "26,033.75"
    def to_float(val):
        if val is None:
            return None
        try:
            return float(str(val).replace(",", ""))
        except:
            return None

    data["nifty_spot"] = to_float(nifty_row["last"])
    data["previous_close"] = to_float(nifty_row["previousClose"])
    data["nifty_high"] = to_float(nifty_row["high"])
    data["nifty_low"] = to_float(nifty_row["low"])
    data["nifty_change"] = to_float(nifty_row["percChange"])

    # 2️⃣ Pre-open / SGX Nifty change
    preopen = safe_call(nse_preopen())
    sgx_nifty_change = None

    try:
        for idx in preopen.get("indices", []):
            if idx.get("symbol") == "NIFTY":
                sgx_nifty_change = idx.get("change")
                break
    except:
        sgx_nifty_change = None

    data["sgx_nifty"] = sgx_nifty_change

    if data["previous_close"] and sgx_nifty_change:
        data["pre_market_change"] = round(
            (sgx_nifty_change / data["previous_close"]) * 100, 2
        )
    else:
        data["pre_market_change"] = None

    # 3️⃣ India VIX
    vix = safe_call(indiavix())
    data["vix"] = vix

    # 4️⃣ Sector sentiment (Bank, IT, Auto)
    sectors = ["NIFTY BANK", "NIFTY IT", "NIFTY AUTO"]
    sector_sentiment = {}

    for sector in sectors:
        row = df[df["indexName"] == sector]
        if not row.empty:
            r = row.iloc[0]
            change = to_float(r["percChange"])
            sector_sentiment[sector.split()[-1]] = "Green" if change > 0 else "Red"
        else:
            sector_sentiment[sector.split()[-1]] = None

    data["sector_sentiment"] = sector_sentiment

    # 5️⃣ Support & Resistance (±1%)
    if data["nifty_spot"]:
        spot = data["nifty_spot"]
        data["support"] = round(spot * 0.995, 2)
        data["resistance"] = round(spot * 1.005, 2)
    else:
        data["support"] = data["resistance"] = None

    # 6️⃣ Return EVERYTHING
    data["nifty_raw"] = nifty_row.to_dict()
    data["all_indices"] = df.to_dict(orient="records")

    return data

def safe_call(func, *args, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func(*args)
        except Exception as e:
            print(f"NSE error: {e}. Retrying {attempt+1}/{retries}...")
            time.sleep(delay)
    return None