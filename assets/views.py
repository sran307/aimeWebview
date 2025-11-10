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


def assets(request):
    return render(request, 'assets/index.html')

def mtftManager(request):
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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
    headings = stockHeadings.objects.all()

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

    transactions = stockTransactions.objects.filter(finYear=finYear.id, transType='SWING')
    data_dict = {(d.heading.id, d.transType): d.transValue for d in transactions}

    context={
        'stockHeadings':headings,
        'data_dict':data_dict
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
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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
    if(processType == 'N'):
        stockTrans = stockTransactions.objects.filter(transType=transType, isProcessed=False)
        rows = (
            stockTransactions.objects
            .filter(transType='SWING', isProcessed=False)
            .select_related('heading')
            .values(
                'refNo',
                'slNo',
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

            grouped_data.setdefault(ref_no, {})
            grouped_data[ref_no].setdefault(sl_no, {})
            grouped_data[ref_no][sl_no][heading] = value

        
        for ref_no, sl_data in grouped_data.items():
            buy_data = None
            sell_data = None
            for sl_no, data in sl_data.items():
                if data.get('transaction') == 'buy':
                    stock_name = getattr(buy_data, 'stockName', None)
                    stock_obj = StockNames.objects.filter(stockName=stock_name).first()
            
                    # Parse dates safely
                    def parse_date(date_str):
                        try:
                            return datetime.strptime(date_str, "%d/%m/%Y").date()
                        except Exception:
                            return None

                    purchased_qty = int(buy_data.get('Quantity') or 0)
                    sell_qty = int(sell_data.get('Quantity') or 0)
                    purchased_rate = int(buy_data.get('Rate') or 0)
                    sell_rate = int(sell_data.get('Rate') or 0)
                    total_purchased = purchased_qty * purchased_rate
                    total_sold = sell_qty * sell_rate
                    profit = total_sold - total_purchased

                    stockDetails.objects.create(
                        finYear_id=1,
                        month_id=11, 
                        stock=stock_obj,
                        purchasedOn=parse_date(buy_data.get('Date')),
                        sellOn=parse_date(sell_data.get('Date')),
                        purchasedQty=purchased_qty,
                        sellQty=sell_qty,
                        purchasedAmnt=purchased_rate,
                        sellAmnt=sell_rate,
                        totalPurchasedAmnt=total_purchased,
                        totalSellAmnt=total_sold,
                        profit=profit,
                        refNo=ref_no,
                        transType=transType,
                    )
                elif data.get('Transaction') == 'sell':
                    sell_data = data

           
                

    return JsonResponse({'status': 'success'})