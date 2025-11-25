import json
from .utils import evaluate_formula
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.contrib.auth.decorators import login_required
import calendar
from datetime import date, datetime
from collections import defaultdict
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from .models import *
from .forms import *

# @login_required
def budgetManager(request):
    today = date.today()

    latest_fy = FinancialYear.objects.order_by("-startDate").first()

    if latest_fy:
        # If current date is within the existing financial year, do nothing
        if today <= latest_fy.endDate:
            fy = latest_fy
            print(f"✅ Current Financial Year still active: {fy.yearDesc}")
        else:
            # Otherwise, create the next financial year
            next_year = int(latest_fy.year) + 1
            next_year_desc = f"{next_year}-{str(next_year + 1)[-2:]}"
            fy = FinancialYear.objects.create(
                year=str(next_year),
                yearDesc=next_year_desc,
                startDate=date(next_year, 4, 1),
                endDate=date(next_year + 1, 3, 31)
            )
            print(f"🆕 Created new Financial Year: {fy.yearDesc}")
    else:
        # No record exists, create the first one
        current_year = today.year
        fy = FinancialYear.objects.create(
            year=str(current_year),
            yearDesc=f"{current_year}-{str(current_year + 1)[-2:]}",
            startDate=date(current_year, 4, 1),
            endDate=date(current_year + 1, 3, 31)
        )
        print(f"🌱 Created initial Financial Year: {fy.yearDesc}")

    return render(request, "budget/index.html")

def monthlyBudget(request):
    earnings = Items.objects.filter(isExpensive=False)
    expenses = Items.objects.filter(isExpensive=True)

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

    existing_data = monthlyData.objects.filter(finYear=finYear.id, month__id=current_month)
    data_dict = {(d.item_id, d.datedOn, d.valueType): d.amount for d in existing_data}

    totals = defaultdict(int)
    for (item_id, date1, valueType), amount in data_dict.items():
        if(valueType == 'MD'):
            totals[item_id] += amount

    expectTotal = defaultdict(int)
    for (item_id, date1, valueType), amount in data_dict.items():
        if(valueType == 'ET'):
            expectTotal[item_id] += amount

    balances = defaultdict(int)
    for item_id in set(list(totals.keys()) + list(expectTotal.keys())):
        balances[item_id] = expectTotal[item_id] - totals[item_id]
    
    totalEarning = defaultdict(int)
    for (item_id, date1, valueType), amount in data_dict.items():
        if(valueType != 'MD' and valueType != 'ET'):
            totalEarning[item_id] += amount

    overall_expected_total = sum(expectTotal.values())
    overall_actual_total = sum(totals.values())
    overall_earnings = sum(totalEarning.values())

    context={
        "earnings":earnings,
        "expenses":expenses,
        'dates':dates, 
        'finYear':finYear, 
        'month':month, 
        'finYears':finYears, 
        'months':months, 
        "data_dict": data_dict, 
        'totals':totals, 
        'expectTotal':expectTotal, 
        'balances':balances, 
        'overall_expected_total':overall_expected_total,
        'overall_actual_total':overall_actual_total, 
        'totalEarning' : totalEarning,
        'overall_earnings' : overall_earnings,
        'expectedBalance':overall_earnings-overall_expected_total,
        'actualBalance':overall_earnings-overall_actual_total

        }
    return render(request, "budget/monthlySheet.html", context)

def addItemModal(request):
    if request.method == "POST":
        form = ItemsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
    else:
        form = ItemsForm()
    return render(request, "items/modal_form.html", {"form": form})

def save_monthly_data(request):
    if request.method == "POST":
        date_str = request.POST.get("date")
        value = request.POST.get("value")
        item_id = request.POST.get("item")
        month_id = request.POST.get("month")
        year_id = request.POST.get("year")
        valueType = request.POST.get("valueType")

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        obj, created = monthlyData.objects.update_or_create(
            finYear_id=year_id,
            month_id=month_id,
            item_id=item_id,
            datedOn=date,
            defaults={"amount": value or 0},
            valueType=valueType
        )
        return JsonResponse({"status": "ok", "created": created})

def debtManager(request):
    debts = DebtManager.objects.all()
    context = {
        'numbers': range(1, 101),
        'debts':debts,
    }
    return render(request, 'budget/debtSheet.html', context)

def debt_form(request, id=None):
    if id:
        debt = get_object_or_404(DebtManager, id=id)
    else:
        debt = None

    if request.method == 'POST':
        form = DebtManagerForm(request.POST, instance=debt)
        if form.is_valid():
            debt_obj = form.save(commit=False)

            if not debt_obj.isPaid:
                debt_obj.debtPaidDate = None

            debt_obj.save()
            return JsonResponse({"status": "success"})
    else:
        form = DebtManagerForm(instance=debt)

    return render(request, 'budget/debt_form.html', {'form': form})

def loanManager(request):
    loans = LoanManager.objects.annotate(
        total_paid=Sum('loanName__amount'),
    ).annotate(
        balance=ExpressionWrapper(
            F('loanAmount') - (F('total_paid')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        totalInt=ExpressionWrapper(
            F('total_paid') - (F('loanAmount')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    loanTrans = LoanTrans.objects.all().order_by('-id')
    context = {
        'loans':loans,
        'loanTrans':loanTrans
    }
    return render(request, 'budget/loanSheet.html', context)

def loan_form(request, id=None):
    loan = get_object_or_404(LoanManager, id=id) if id else None

    if request.method == 'POST':
        form = LoanManagerForm(request.POST, instance=loan)
        if form.is_valid():
            loan_obj = form.save(commit=False)

            # If loan not closed, make sure paid date is None
            if not loan_obj.isClosed:
                loan_obj.loanPaidDate = None
            else:
                # Optional: Auto-set today’s date when loan is closed and no paid date entered
                if not loan_obj.loanPaidDate:
                    loan_obj.loanPaidDate = date.today()

            loan_obj.save()
            return JsonResponse({"status": "success"})
    else:
        form = LoanManagerForm(instance=loan)

    return render(request, 'budget/loan_form.html', {'form': form})


def monthlyBudgetSheet(request):
    finYear=FinancialYear.objects.order_by("-id").first()
    current_month = date.today().month
    month = Months.objects.get(id=current_month)
    
    sheet, created = Sheet.objects.get_or_create(
        finYear=finYear,
        month_id=current_month,  
        defaults={'name': f'{month.monthAbbr} {finYear.yearDesc}'}
    )

    # pass basic metadata (you can change grid size as needed)
    context = {"sheet": sheet, "rows": range(1, 41), "cols": range(1, 11)}
    return render(request, "budget/sheet.html", context)


# @login_required
@require_GET
def load_sheet(request, sheet_id):
    sheet = get_object_or_404(Sheet, id=sheet_id)
    cells = Cell.objects.filter(sheet=sheet)
    data = {}
    for c in cells:
        data[f"{c.row}:{c.col}"] = {"value": c.value, "version": c.version}
    return JsonResponse({"status": "ok", "cells": data})


# @login_required
@require_POST
def save_cell(request):
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        sheet_id = int(payload.get("sheet_id"))
        row = int(payload.get("row"))
        col = int(payload.get("col"))
        value = payload.get("value", "")
        client_version = payload.get("version", 0)

        sheet = get_object_or_404(Sheet, id=sheet_id)
    
        # ✅ If formula
        if value and value.startswith("="):
            formula = value
            result = evaluate_formula(sheet, formula)
            cell, _ = Cell.objects.update_or_create(
                sheet=sheet, row=row, col=col,
                defaults={'formula': formula, 'value': result}
            )
        else:
            # Regular value
            cell, _ = Cell.objects.update_or_create(
                sheet=sheet, row=row, col=col,
                defaults={'formula': None, 'value': value}
            )

        # ✅ Recalculate dependent cells
        cell_ref = f"{chr(64 + col)}{row}"
        dependents = Cell.objects.filter(sheet=sheet, formula__icontains=cell_ref)
        for dep in dependents:
            dep.value = evaluate_formula(sheet, dep.formula)
            dep.save(update_fields=["value"])
        return JsonResponse({"status": "success", "value": cell.value})

@require_POST
def show_formula(request):
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        sheet_id = int(payload.get("sheet_id"))
        row = int(payload.get("row"))
        col = int(payload.get("col"))
        value = payload.get("value", "")
        client_version = payload.get("version", 0)

        # sheet = get_object_or_404(Sheet, id=sheet_id)
           
        try:
            cell = Cell.objects.get(sheet=sheet_id, row=row, col=col)
            print(cell)
            if(cell.formula):
                return JsonResponse({
                    "status": "success",
                    "value": cell.value,      # evaluated value
                    "formula": cell.formula   # None if not a formula
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "value": "",
                    "formula": None
                })
        except Cell.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "value": "",
                "formula": None
            })

def loanTrans(request):
    if request.method == 'POST':
        form = LoanTransForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})  # change as needed
    else:
        form = LoanTransForm()

    return render(request, 'budget/loan_form.html', {'form': form})