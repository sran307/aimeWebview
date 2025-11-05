import json
from .utils import evaluate_formula
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.contrib.auth.decorators import login_required
from datetime import date

from .models import Sheet, Cell, CellChange, FinancialYear, Months

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
# def save_cell(request):
#     """
#     Expect JSON body:
#     {
#       "sheet_id": 1,
#       "row": 3,
#       "col": 4,
#       "value": "Hello",
#       "version": 2   # optional; client version
#     }
#     """
#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#         sheet_id = int(payload.get("sheet_id"))
#         row = int(payload.get("row"))
#         col = int(payload.get("col"))
#         new_value = payload.get("value", "")
#         client_version = int(payload.get("version", 0))
#     except Exception:
#         return HttpResponseBadRequest("invalid request")

#     sheet = get_object_or_404(Sheet, id=sheet_id)

#     with transaction.atomic():
#         # lock the cell row (if exists) to avoid race; get_or_create in the same transaction
#         cell, created = Cell.objects.select_for_update().get_or_create(
#             sheet=sheet, row=row, col=col,
#             defaults={"value": new_value, "version": 1},
#         )

#         if not created:
#             # conflict detection (optimistic)
#             if client_version and client_version != cell.version:
#                 # let client know there's a version mismatch (409 semantics)
#                 return JsonResponse({
#                     "status": "conflict",
#                     "server_value": cell.value,
#                     "server_version": cell.version,
#                 }, status=409)

#             # record change
#             old = cell.value
#             if old != new_value:
#                 cell.value = new_value
#                 cell.version += 1
#                 cell.save(update_fields=["value", "version", "updated_at"])
#                 CellChange.objects.create(
#                     cell=cell, old_value=old, new_value=new_value,
#                     version=cell.version
#                 )

#     return JsonResponse({"status": "ok", "version": cell.version})
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