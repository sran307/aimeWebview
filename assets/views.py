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