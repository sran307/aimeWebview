from django.shortcuts import render
from .models import *
from budgetManager.models import *
import calendar
from datetime import date, datetime
from collections import defaultdict
from django.http import JsonResponse, HttpResponseBadRequest


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
        date_str = request.POST.get("date")
        value = request.POST.get("value")
        item_id = request.POST.get("item")
        month_id = request.POST.get("month")
        year_id = request.POST.get("year")
        valueType = request.POST.get("valueType")

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        obj, created = stockTransactions.objects.update_or_create(
            finYear_id=year_id,
            month_id=month_id,
            heading_id=item_id,
            transDate=date,
            defaults={"transValue": value or ''},
            transType=valueType
        )
        return JsonResponse({"status": "ok", "created": created})

def swingManager(request):
    headings = stockHeadings.objects.all()
    context={
        'stockHeadings':headings
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