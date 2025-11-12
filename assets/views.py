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

def assets(request):
    return render(request, 'assets/index.html')

def mtftManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='MTFT')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/mtft.html', context)

def mtftTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='MTFT')
    data_dict = {(d.heading.id, d.transDate, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
    }
    return render(request, 'assets/mtftTrans.html', context)

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

def swingManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='SWING')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/swing.html', context)

def swingTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='SWING')
    data_dict = {}

    for d in transactions:
        key = (d.heading.id, d.slNo, d.transType)
        data_dict[key] = d.transValue

        data_dict[('reference', d.slNo, d.transType)] = d.refNo


    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
        'numbers': range(1, 101),
    }
    return render(request, 'assets/swingTrans.html', context)


def intraManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='INTRA')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/intra.html', context)

def intraTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='INTRA')
    data_dict = {(d.heading.id, d.transDate, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
    }
    return render(request, 'assets/intraTrans.html', context)

def longManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='LONG')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/long.html', context)

def longTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='LONG')
    data_dict = {(d.heading.id, d.transDate, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
    }
    return render(request, 'assets/longTrans.html', context)

def optionManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='OPTION')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/option.html', context)

def optionTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='OPTION')
    data_dict = {(d.heading.id, d.transDate, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
    }
    return render(request, 'assets/optionTrans.html', context)

def showStocks(request):
    stocks = StockNames.objects.all()
    context={
        'stocks':stocks
    }
    return render(request, 'assets/showStocks.html', context)

def mfManager(request):
    selected_year_id = request.GET.get('year') 
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    
    finYears = FinancialYear.objects.all()

    stockData = stockDetails.objects.filter(buyFinYear=finYear.id, transType='MF')

    context={
        'stockDetails':stockData
    }
    return render(request, 'assets/mf.html', context)

def mfTransactions(request):
    selected_year_id = request.GET.get('year') 
    selected_month_id = request.GET.get('month')
    if(selected_year_id):
        finYear=FinancialYear.objects.get(id=selected_year_id)
    else:
        finYear=FinancialYear.objects.order_by("-id").first()
    if(selected_month_id):
        current_month = Months.objects.get(id=selected_month_id).id
    else:
        current_month = date.today().month
    month = Months.objects.get(id=current_month)

    months = Months.objects.all()
    finYears = FinancialYear.objects.all()
   
    
    days = calendar.monthrange(int(finYear.year), current_month)[1]
    dates = [date(int(finYear.year), current_month, d) for d in range(1, days + 1)]

    headings = stockHeadings.objects.all()

    transactions = stockTransactions.objects.filter(finYear=finYear.id, month__id=current_month, transType='MF')
    data_dict = {(d.heading.id, d.transDate, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'dates':dates,
        'month':month,
        'finYear':finYear,
        'months':months,
        'finYears':finYears,
        'data_dict':data_dict,
    }
    return render(request, 'assets/mfTrans.html', context)

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
                pprint(buy_data)
                stock_name = buy_data.get('stockName')
                stock_obj = StockNames.objects.filter(stockName=stock_name).first()

                purchased_qty = int(buy_data.get('quantity') or 0)
                purchased_rate = int(buy_data.get('amntPerStock') or 0)
                purchasedBrkg = int(buy_data.get('brockerage') or 0)
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
                        'buyFinYear':finYear
                    }
                )
            if transaction_type == 'sell':
                sell_data = data
                stock_name = sell_data.get('stockName')
                stock_obj = StockNames.objects.filter(stockName=stock_name).first()
                sell_qty = int(sell_data.get('quantity') or 0)
                sell_rate = int(sell_data.get('amntPerStock') or 0)
                sellBrkg = int(buy_data.get('brockerage') or 0)

                total_sold = (sell_qty * sell_rate)-sellBrkg
                sellReason = sell_data.get('sellReason') or ''
                sellRemarks = sell_data.get('remarks') or ''
                sellYear = buy_data.get('finYear') or ''
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
                        'sellFinYear':finYear
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
    return JsonResponse({'status':'error', 'message': 'ERROR all the data processed'})
    